import streamlit as st 
import openai
from langchain.llms import OpenAI
from models import Story, CharacterModel, generate_image
from contants import MODEL_NAME, TEMPERATURE


class Layout:

    def __init__(self):
        self.header = st.container()
        self.characters = st.container()
        self.outline = st.container()
        self.text = st.container()
        self.appendix = st.container()

        self.character = None
        self.character_img_cols= []

        self.characters.write("## Starring")
        self.outline.write("## Contents")
        self.text.write("## Story")       
        self.appendix.write("## Logs")


    def add_log(self, story):
        self.appendix.write("\n")
        self.appendix.code(story.json(indent=4), language="json")

    def add_metadata(self, story):
        self.header.write(f"# {story.metadata.title}")
        self.header.write(f"By {story.metadata.author}")
        self.add_log(story)

    def add_character(self, i, character: CharacterModel):
        col1, col2 = self.character[i].columns([1,2])
        self.character_img_cols.append(col1)
        col2.write(f"## {character.name}")
        col2.write(character.personality)

    def add_characters(self, story: Story):
        self.character = [self.characters.container() for _ in story.characters.characters]
        for i, character in enumerate(story.characters.characters):
            self.add_character(i, character)
    
        self.add_log(story) 

    def add_outline(self, story: Story):
        for outline in story.outline.outlines:
            self.outline.write(f"**Chapter {outline.chapter}**: {outline.title}")
        self.add_log(story)

    def add_text(self, story: Story):
        for i, chapter in enumerate(story.text.chapters):
            self.text.write(f"### Chapter {chapter.chapter}: {story.outline.outlines[i].title}")
            self.text.write(chapter.text)
            self.add_log(story)

    def add_character_img(self, i, url):
        self.character_img_cols[i].image(url)

st.title("📚 Childrens' storybook generator")
key = st.text_input(label="Enter your OpenAI API key")
if key: 
    openai.api_key = key
    llm = OpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE, openai_api_key=key, max_tokens=2048)

    prompt = st.text_input(label="Enter a prompt for a childrens' book")
    if prompt:

        layout = Layout()
        story = Story(prompt=prompt)

        ## metadata 
        story.add_metadata(llm)
        layout.add_metadata(story)

        ## characters
        story.add_characters(llm)
        layout.add_characters(story)
        for i, _ in enumerate(story.characters.characters):
            prompt, response = generate_image(openai, llm, story, i)
            layout.add_character_img(i, response.data[0].url)

            layout.appendix.write("Character image: ")
            layout.appendix.write(prompt)
            layout.appendix.code(response, language="json")

        ## outline 
        story.add_outline(llm)
        layout.add_outline(story)

        ## text
        story.add_text(llm)
        layout.add_text(story)
