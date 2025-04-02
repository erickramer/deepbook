"""
Data models for the DeepBook application.

This module defines the structure of the story components using Pydantic models.
Each model represents a different part of the children's book.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.prompts import IMG_TEMPLATE, TEMPLATE, TEXT_TEMPLATE


class Model(BaseModel):
    """Base model class that all other models inherit from."""

    pass


class MetaDataModel(Model):
    """Model for storing book metadata information."""

    title: str = Field(
        description="the title of the children's book",
    )
    author: str = Field(description="the whimsical and fantasical name for the author")
    year: int = Field(description="the year the book was published in the past or future!")
    themes: List[str] = Field(description="themes touched upon by the book")
    location: str = Field(description="the place where the majority of the story takes place")


class ChapterOutlineModel(Model):
    """Model for individual chapter outline information."""

    chapter: int = Field(description="The number of the chapter")
    title: str = Field(description="The title of the chapter")
    synopsis: str = Field(description="1-2 sentence summary of the chapter")


class BookOutlineModel(Model):
    """Model for the overall book outline containing plot structure and chapter outlines."""

    synopsis: str = Field(description="1-2 sentence summary of the book")
    conflict: str = Field(
        description="The specific conflict that must be resolved or obstacle that must be overcome"
    )
    resolution: str = Field(
        description="The specific way the conflict is resolved (who, how and when)"
    )
    outlines: List[ChapterOutlineModel] = Field(
        description="List of outlines for individual chapters"
    )


class CharacterModel(Model):
    """Model for storing individual character information."""

    name: str = Field(description="name of the character")
    description: str = Field(description="physical description of the character")
    personality: str = Field(description="a one sentence biography of the character")


class CharactersModel(Model):
    """Model for storing all characters in the story."""

    characters: List[CharacterModel]


class ChapterTextModel(Model):
    """Model for storing the full text content of a single chapter."""

    chapter: int = Field("")
    text: str = Field(
        "The text for the chapter. This is the text that is read to children. It should read like a children's book and follow the synopsis in the outline"
    )


class FullTextModel(Model):
    """Model for storing the full text content of all chapters in the book."""

    chapters: List[ChapterTextModel] = []


class Story(Model):
    """Main model that orchestrates the entire story generation process.

    Contains all components of the children's book, including metadata,
    characters, outline, and full text content.
    """

    prompt: str = Field(description="A human entered prompt to start the story generation")
    metadata: Optional[MetaDataModel]
    characters: Optional[CharactersModel]
    outline: Optional[BookOutlineModel]
    text: Optional[FullTextModel]

    def _run_llm(self, llm, model: type[Model], name, template=TEMPLATE):
        """Internal helper method to run a language model with a specific prompt template.

        Args:
            llm: The language model to use for generation
            model: The Pydantic model class to parse the output into
            name: The name of the field being generated
            template: The prompt template to use (defaults to TEMPLATE)

        Returns:
            An instance of the specified model populated with the generated content
        """
        parser = PydanticOutputParser(pydantic_object=model)
        prompt = PromptTemplate(
            template=template,
            input_variables=["story"],
            partial_variables={"instructions": parser.get_format_instructions(), "name": name},
        )
        output = llm(prompt.format_prompt(story=self.json()).to_string())
        return parser.parse(output)

    def add_metadata(self, llm):
        """Generate metadata for the story including title, author, and themes.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.metadata = self._run_llm(llm, MetaDataModel, "metadata")
        return self

    async def add_metadata_async(self, llm):
        """Generate metadata for the story asynchronously.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.metadata = await asyncio.to_thread(self._run_llm, llm, MetaDataModel, "metadata")
        return self

    def add_characters(self, llm):
        """Generate character definitions for the story.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.characters = self._run_llm(llm, CharactersModel, "characters")
        return self

    async def add_characters_async(self, llm):
        """Generate character definitions for the story asynchronously.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.characters = await asyncio.to_thread(self._run_llm, llm, CharactersModel, "characters")
        return self

    def add_outline(self, llm):
        """Generate a story outline including chapter structure.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.outline = self._run_llm(llm, BookOutlineModel, "outline")
        return self

    async def add_outline_async(self, llm):
        """Generate a story outline asynchronously.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.outline = await asyncio.to_thread(self._run_llm, llm, BookOutlineModel, "outline")
        return self

    def add_text(self, llm):
        """Generate the full text content for each chapter in the story.

        Iterates through each chapter outline and generates the complete
        text content for that chapter.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.text = FullTextModel()

        for outline in self.outline.outlines:
            res = self._run_llm(llm, ChapterTextModel, outline.chapter, TEXT_TEMPLATE)
            self.text.chapters.append(res)

        return self

    async def add_text_async(self, llm):
        """Generate the full text content for all chapters concurrently.

        Generates text for all chapters at the same time for better performance.

        Args:
            llm: The language model to use for generation

        Returns:
            Self for method chaining
        """
        self.text = FullTextModel()

        async def generate_chapter_text(outline):
            # Currently there's no async version of LangChain's run, so we use
            # asyncio.to_thread to run it in a separate thread without blocking
            chapter_text = await asyncio.to_thread(
                self._run_llm, llm, ChapterTextModel, outline.chapter, TEXT_TEMPLATE
            )
            return outline.chapter, chapter_text

        # Create a task for each chapter
        tasks = []
        for outline in self.outline.outlines:
            task = generate_chapter_text(outline)
            tasks.append(task)

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)

        # Sort results by chapter number and add to text
        sorted_results = sorted(results, key=lambda x: x[0])
        for _, chapter_text in sorted_results:
            self.text.chapters.append(chapter_text)

        return self


async def generate_image_async(openai, llm, story: Story, i: int):
    """Generate a high-quality character illustration using OpenAI's DALL-E 3 (asynchronously).

    Uses a language model to create a detailed descriptive prompt based on the character,
    then passes that prompt to OpenAI's DALL-E 3 image generation API with enhanced styling.

    The function generates illustrations with:
    - Consistent children's book illustration style
    - Whimsical, colorful watercolor aesthetic
    - Detailed backgrounds and gentle color palette
    - High-definition 1024x1024 resolution

    Args:
        openai: The OpenAI client for making API calls
        llm: The language model to use for prompt generation
        story: The Story object containing character information
        i: The index of the character to generate an image for

    Returns:
        Tuple containing (character index, generated prompt text, OpenAI image response)
    """
    prompt = PromptTemplate(
        template=IMG_TEMPLATE,
        input_variables=["story", "i", "character"],
    )

    s = prompt.format_prompt(
        story=story.json(), i=i, character=story.characters.characters[i]
    ).to_string()
    res = llm(s)

    # Style descriptors for consistent, high-quality children's book illustrations
    style_descriptors = [
        "whimsical",
        "colorful",
        "watercolor style",
        "children's book illustration",
        "cute and friendly",
        "detailed background",
        "gentle color palette",
    ]

    style_text = ", ".join(style_descriptors)

    # Use DALL-E 3 with larger size and HD quality
    response = await openai.Image.acreate(
        prompt=f"A children's book illustration in {style_text} style. {res}",
        n=1,
        size="1024x1024",
        model="dall-e-3",
        quality="hd",
    )

    return i, res, response


def generate_image(openai, llm, story: Story, i: int):
    """Synchronous wrapper for generate_image_async for backward compatibility.

    Args:
        openai: The OpenAI client for making API calls
        llm: The language model to use for prompt generation
        story: The Story object containing character information
        i: The index of the character to generate an image for

    Returns:
        Tuple containing (generated prompt text, OpenAI image response)
    """
    loop = asyncio.get_event_loop()
    try:
        _, prompt, response = loop.run_until_complete(generate_image_async(openai, llm, story, i))
    except RuntimeError:
        # If there's no event loop in the current thread, create and use a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _, prompt, response = loop.run_until_complete(generate_image_async(openai, llm, story, i))
        loop.close()
    return prompt, response


async def generate_all_character_images(
    openai, llm, story: Story
) -> List[Tuple[int, str, Dict[str, Any]]]:
    """Generate illustrations for all characters concurrently.

    Args:
        openai: The OpenAI client for making API calls
        llm: The language model to use for prompt generation
        story: The Story object containing character information

    Returns:
        List of tuples containing (character index, generated prompt text, OpenAI image response)
    """
    tasks = []
    for i, _ in enumerate(story.characters.characters):
        task = generate_image_async(openai, llm, story, i)
        tasks.append(task)

    # Run all image generation tasks concurrently
    results = await asyncio.gather(*tasks)

    return results
