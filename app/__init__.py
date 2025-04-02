"""
Main application module for DeepBook - a children's storybook generator.

This module provides the Streamlit interface and coordinates the story generation process.
"""

import asyncio

import openai
import streamlit as st
from langchain.llms import OpenAI

from app.contants import MODEL_NAME, TEMPERATURE
from app.models import CharacterModel, Story, generate_all_character_images


class Layout:
    """Manages the Streamlit UI layout and rendering of story elements.

    This class creates containers for each section of the storybook and
    provides methods to add content to these sections.
    """

    def __init__(self):
        """Initialize the layout containers and section headers."""
        self.header = st.container()
        self.characters = st.container()
        self.outline = st.container()
        self.text = st.container()
        self.appendix = st.container()

        self.character = None
        self.character_img_cols = []

        self.characters.write("## Starring")
        self.outline.write("## Contents")
        self.text.write("## Story")
        self.appendix.write("## Logs")

    def add_log(self, story):
        """Add JSON representation of the story to the logs section.

        Args:
            story: The Story object to display in the logs
        """
        self.appendix.write("\n")
        self.appendix.code(story.json(indent=4), language="json")

    def add_metadata(self, story):
        """Add book title and author to the header section.

        Args:
            story: The Story object containing metadata
        """
        self.header.write(f"# {story.metadata.title}")
        self.header.write(f"By {story.metadata.author}")
        self.add_log(story)

    def add_character(self, i, character: CharacterModel):
        """Add a single character to the characters section.

        Creates a two-column layout with space for the character image
        and the character details.

        Args:
            i: The index of the character
            character: The CharacterModel object to display
        """
        col1, col2 = self.character[i].columns([1, 2])
        self.character_img_cols.append(col1)
        col2.write(f"## {character.name}")
        col2.write(character.personality)

    def add_characters(self, story: Story):
        """Add all characters to the characters section.

        Creates a container for each character and adds them to the UI.

        Args:
            story: The Story object containing characters
        """
        self.character = [self.characters.container() for _ in story.characters.characters]
        for i, character in enumerate(story.characters.characters):
            self.add_character(i, character)

        self.add_log(story)

    def add_outline(self, story: Story):
        """Add chapter outlines to the contents section.

        Displays a list of chapter titles in the table of contents.

        Args:
            story: The Story object containing the outline
        """
        for outline in story.outline.outlines:
            self.outline.write(f"**Chapter {outline.chapter}**: {outline.title}")
        self.add_log(story)

    def add_text(self, story: Story):
        """Add full text content for each chapter to the story section.

        Displays chapter titles and full text content for each chapter.

        Args:
            story: The Story object containing the text
        """
        for i, chapter in enumerate(story.text.chapters):
            self.text.write(f"### Chapter {chapter.chapter}: {story.outline.outlines[i].title}")
            self.text.write(chapter.text)
            self.add_log(story)

    def add_character_img(self, i, url):
        """Add a character illustration to the characters section.

        Args:
            i: The index of the character
            url: The URL of the generated image
        """
        self.character_img_cols[i].image(url)


def run_app():
    """Main entry point for the DeepBook application."""
    st.set_page_config(page_title="📚 Childrens' storybook generator")
    st.title("📚 Childrens' storybook generator")
    key = st.text_input(label="Enter your OpenAI API key")
    if key:
        openai.api_key = key
        llm = OpenAI(
            model_name=MODEL_NAME, temperature=TEMPERATURE, openai_api_key=key, max_tokens=2048
        )

        prompt = st.text_input(label="Enter a prompt for a childrens' book")
        if prompt:
            layout = Layout()
            story = Story(prompt=prompt)

            # metadata - generate asynchronously
            with st.spinner("Generating story metadata..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                await_story = loop.run_until_complete(story.add_metadata_async(llm))
                loop.close()

            layout.add_metadata(story)

            # characters - generate asynchronously
            with st.spinner("Generating characters..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                await_story = loop.run_until_complete(story.add_characters_async(llm))
                loop.close()

            layout.add_characters(story)

            # Generate all character images concurrently
            with st.spinner("Generating character illustrations..."):
                # Run the async function inside an asyncio event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                images = loop.run_until_complete(generate_all_character_images(openai, llm, story))
                loop.close()

            # Display all generated images
            for i, prompt, response in images:
                layout.add_character_img(i, response["data"][0]["url"])
                layout.appendix.write("Character image: ")
                layout.appendix.write(prompt)
                layout.appendix.code(response, language="json")

            # outline - generate asynchronously
            with st.spinner("Generating story outline..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                await_story = loop.run_until_complete(story.add_outline_async(llm))
                loop.close()

            layout.add_outline(story)

            # text - generate all chapters in parallel
            with st.spinner("Generating story text..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                await_story = loop.run_until_complete(story.add_text_async(llm))
                loop.close()

            layout.add_text(story)


if __name__ == "__main__":
    run_app()
