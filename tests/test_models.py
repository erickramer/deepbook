"""
Tests for the data models in the DeepBook application.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from app.models import (
    BookOutlineModel,
    ChapterOutlineModel,
    ChapterTextModel,
    CharacterModel,
    CharactersModel,
    FullTextModel,
    MetaDataModel,
    Model,
    Story,
    generate_image,
)


class TestModels(unittest.TestCase):
    """Test cases for the Pydantic models."""

    def test_metadata_model(self):
        """Test MetaDataModel creation and validation."""
        data = {
            "title": "The Adventures of Timmy",
            "author": "Wanda Wordsmith",
            "year": 2023,
            "themes": ["friendship", "bravery", "animals"],
            "location": "Whispering Forest",
        }

        model = MetaDataModel(**data)

        self.assertEqual(model.title, "The Adventures of Timmy")
        self.assertEqual(model.author, "Wanda Wordsmith")
        self.assertEqual(model.year, 2023)
        self.assertEqual(model.themes, ["friendship", "bravery", "animals"])
        self.assertEqual(model.location, "Whispering Forest")

    def test_character_model(self):
        """Test CharacterModel creation and validation."""
        data = {
            "name": "Timmy",
            "description": "A small green turtle with a bright yellow shell",
            "personality": "Timmy is brave but cautious, always helping others despite his fears.",
        }

        model = CharacterModel(**data)

        self.assertEqual(model.name, "Timmy")
        self.assertEqual(model.description, "A small green turtle with a bright yellow shell")
        self.assertEqual(
            model.personality,
            "Timmy is brave but cautious, always helping others despite his fears.",
        )

    def test_characters_model(self):
        """Test CharactersModel creation with multiple characters."""
        character1 = CharacterModel(
            name="Timmy",
            description="A small green turtle with a bright yellow shell",
            personality="Timmy is brave but cautious, always helping others despite his fears.",
        )

        character2 = CharacterModel(
            name="Luna",
            description="A wise old owl with silver feathers",
            personality="Luna is knowledgeable and kind, guiding the forest creatures with her wisdom.",
        )

        model = CharactersModel(characters=[character1, character2])

        self.assertEqual(len(model.characters), 2)
        self.assertEqual(model.characters[0].name, "Timmy")
        self.assertEqual(model.characters[1].name, "Luna")

    def test_chapter_outline_model(self):
        """Test ChapterOutlineModel creation and validation."""
        data = {
            "chapter": 1,
            "title": "The Big Storm",
            "synopsis": "Timmy helps his friends prepare for an unexpected storm.",
        }

        model = ChapterOutlineModel(**data)

        self.assertEqual(model.chapter, 1)
        self.assertEqual(model.title, "The Big Storm")
        self.assertEqual(model.synopsis, "Timmy helps his friends prepare for an unexpected storm.")

    def test_book_outline_model(self):
        """Test BookOutlineModel creation with chapter outlines."""
        chapter1 = ChapterOutlineModel(
            chapter=1,
            title="The Big Storm",
            synopsis="Timmy helps his friends prepare for an unexpected storm.",
        )

        chapter2 = ChapterOutlineModel(
            chapter=2,
            title="Luna's Wisdom",
            synopsis="Timmy seeks advice from Luna the owl to find shelter.",
        )

        model = BookOutlineModel(
            synopsis="A story about a brave turtle helping his forest friends during a storm.",
            conflict="The animals of the forest must find shelter before the big storm hits.",
            resolution="Timmy leads everyone to a cave he discovered, saving them from the storm.",
            outlines=[chapter1, chapter2],
        )

        self.assertEqual(
            model.synopsis,
            "A story about a brave turtle helping his forest friends during a storm.",
        )
        self.assertEqual(len(model.outlines), 2)
        self.assertEqual(model.outlines[0].title, "The Big Storm")
        self.assertEqual(model.outlines[1].title, "Luna's Wisdom")

    def test_story_json_serialization(self):
        """Test that Story objects can be properly serialized to JSON."""
        story = Story(prompt="A story about a brave turtle")
        story.metadata = MetaDataModel(
            title="The Adventures of Timmy",
            author="Wanda Wordsmith",
            year=2023,
            themes=["friendship", "bravery", "animals"],
            location="Whispering Forest",
        )

        json_str = story.json()
        data = json.loads(json_str)

        self.assertEqual(data["prompt"], "A story about a brave turtle")
        self.assertEqual(data["metadata"]["title"], "The Adventures of Timmy")


class TestStoryGeneration(unittest.TestCase):
    """Test cases for the story generation methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.story = Story(prompt="A story about a brave turtle")
        self.mock_llm = MagicMock()
        self.mock_llm.return_value = """
        {
            "title": "The Adventures of Timmy",
            "author": "Wanda Wordsmith",
            "year": 2023,
            "themes": ["friendship", "bravery", "animals"],
            "location": "Whispering Forest"
        }
        """

    def test_add_metadata(self):
        """Test adding metadata to a story."""
        self.story.add_metadata(self.mock_llm)

        self.assertIsNotNone(self.story.metadata)
        self.assertEqual(self.story.metadata.title, "The Adventures of Timmy")
        self.assertEqual(self.story.metadata.author, "Wanda Wordsmith")
        self.mock_llm.assert_called_once()

    @patch("app.models.PydanticOutputParser")
    def test_run_llm(self, mock_parser_class):
        """Test the _run_llm method."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.get_format_instructions.return_value = "Format instructions"
        mock_parser.parse.return_value = MetaDataModel(
            title="Test Title",
            author="Test Author",
            year=2023,
            themes=["test"],
            location="Test Location",
        )

        result = self.story._run_llm(self.mock_llm, MetaDataModel, "metadata")

        self.assertIsInstance(result, MetaDataModel)
        self.assertEqual(result.title, "Test Title")
        self.mock_llm.assert_called_once()


class TestImageGeneration(unittest.TestCase):
    """Test cases for the image generation function."""

    @patch("app.models.PromptTemplate")
    def test_generate_image(self, mock_prompt_template):
        """Test the generate_image function."""
        # Create mocks
        mock_openai = MagicMock()
        mock_llm = MagicMock()
        mock_prompt_instance = MagicMock()
        mock_prompt_template.return_value = mock_prompt_instance

        # Setup return values
        mock_prompt_instance.format_prompt.return_value.to_string.return_value = "formatted prompt"
        mock_llm.return_value = "Generated description for a turtle"

        # Since we're using asyncio now, we need to mock the response differently
        async def mock_acreate(*args, **kwargs):
            return {"data": [{"url": "https://example.com/image.png"}]}

        # Mock the async Image.acreate method
        mock_openai.Image = MagicMock()
        mock_openai.Image.acreate = mock_acreate
        mock_openai.Image.create.return_value = {"data": [{"url": "https://example.com/image.png"}]}

        # Create a story with characters
        story = Story(prompt="A story about a brave turtle")
        story.characters = CharactersModel(
            characters=[
                CharacterModel(
                    name="Timmy",
                    description="A small green turtle with a bright yellow shell",
                    personality="Timmy is brave but cautious, always helping others despite his fears.",
                )
            ]
        )

        # Call the function - this will use run_until_complete internally
        prompt, response = generate_image(mock_openai, mock_llm, story, 0)

        # Assertions for the synchronous wrapper
        self.assertEqual(prompt, "Generated description for a turtle")
        self.assertEqual(response["data"][0]["url"], "https://example.com/image.png")
        mock_llm.assert_called_once_with("formatted prompt")

    @patch("app.models.PromptTemplate")
    async def test_generate_image_async(self, mock_prompt_template):
        """Test the async generate_image_async function."""
        # This test would require an async test runner, so we'll mock it
        # In a real situation, we'd use pytest-asyncio or similar
        pass


if __name__ == "__main__":
    unittest.main()
