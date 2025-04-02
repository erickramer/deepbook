"""
Tests for the image quality improvements using DALL-E 3.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from app.models import CharacterModel, CharactersModel, Story, generate_image_async


class TestImageQuality(unittest.TestCase):
    """Test cases for the DALL-E 3 image generation improvements."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a story with a character
        self.story = Story(prompt="A test story")
        self.story.characters = CharactersModel(
            characters=[
                CharacterModel(
                    name="Test Character",
                    description="A friendly blue robot with round eyes",
                    personality="Curious and helpful",
                )
            ]
        )

        # Mock objects
        self.mock_openai = MagicMock()
        self.mock_llm = MagicMock()

        # Setup the async method to return a valid response
        async def mock_acreate(*args, **kwargs):
            return {"data": [{"url": "https://example.com/image.png"}]}

        self.mock_openai.Image.acreate = mock_acreate

    @patch("app.models.PromptTemplate")
    async def test_dalle3_parameters(self, mock_prompt_template):
        """Test that DALL-E 3 is called with the correct parameters."""
        # Setup the prompt template mock
        mock_prompt_instance = MagicMock()
        mock_prompt_template.return_value = mock_prompt_instance
        mock_prompt_instance.format_prompt.return_value.to_string.return_value = "formatted prompt"

        # Set up the LLM response
        self.mock_llm.return_value = "Generated character description"

        # Mock the acreate method with an implementation that checks parameters
        acreate_called_with = {}

        async def check_acreate_params(*args, **kwargs):
            nonlocal acreate_called_with
            acreate_called_with = kwargs
            return {"data": [{"url": "https://example.com/image.png"}]}

        self.mock_openai.Image.acreate = check_acreate_params

        # Call the function
        await generate_image_async(self.mock_openai, self.mock_llm, self.story, 0)

        # Verify that DALL-E 3 is called with the expected parameters
        self.assertEqual(acreate_called_with["model"], "dall-e-3")
        self.assertEqual(acreate_called_with["size"], "1024x1024")
        self.assertEqual(acreate_called_with["quality"], "hd")
        self.assertEqual(acreate_called_with["n"], 1)

    @patch("app.models.PromptTemplate")
    async def test_style_descriptors(self, mock_prompt_template):
        """Test that style descriptors are included in the prompt."""
        # Setup
        mock_prompt_instance = MagicMock()
        mock_prompt_template.return_value = mock_prompt_instance
        mock_prompt_instance.format_prompt.return_value.to_string.return_value = "formatted prompt"

        # Set up the LLM response
        self.mock_llm.return_value = "Generated character description"

        # Create a variable to capture the prompt
        prompt_used = None

        # Mock the acreate method to capture the prompt
        async def capture_prompt(*args, **kwargs):
            nonlocal prompt_used
            prompt_used = kwargs.get("prompt", "")
            return {"data": [{"url": "https://example.com/image.png"}]}

        self.mock_openai.Image.acreate = capture_prompt

        # Call the function
        await generate_image_async(self.mock_openai, self.mock_llm, self.story, 0)

        # Check that the prompt includes all style descriptors
        style_descriptors = [
            "whimsical",
            "colorful",
            "watercolor style",
            "children's book illustration",
            "cute and friendly",
            "detailed background",
            "gentle color palette",
        ]

        for descriptor in style_descriptors:
            self.assertIn(descriptor, prompt_used)

        # Also check that the LLM-generated description is included
        self.assertIn("Generated character description", prompt_used)

    @patch("app.prompts.IMG_TEMPLATE")
    @patch("app.models.PromptTemplate")
    async def test_detailed_prompt_template(self, mock_prompt_template, mock_img_template):
        """Test that the detailed prompt template is used."""
        # Setup
        from app.prompts import IMG_TEMPLATE

        # Verify that the template includes the detailed requirements
        self.assertIn("physical appearance", IMG_TEMPLATE)
        self.assertIn("facial features", IMG_TEMPLATE)
        self.assertIn("clothing and accessories", IMG_TEMPLATE)
        self.assertIn("pose or action", IMG_TEMPLATE)
        self.assertIn("background elements", IMG_TEMPLATE)
        self.assertIn("mood and atmosphere", IMG_TEMPLATE)

        # Also test that the prompt template is called with the right values
        mock_prompt_instance = MagicMock()
        mock_prompt_template.return_value = mock_prompt_instance

        # Set up the mock to capture the template used
        def capture_template(*args, **kwargs):
            self.assertEqual(kwargs.get("template"), IMG_TEMPLATE)
            return mock_prompt_instance

        mock_prompt_template.side_effect = capture_template

        # Mock the rest of the calls
        mock_prompt_instance.format_prompt.return_value.to_string.return_value = "formatted prompt"
        self.mock_llm.return_value = "Generated character description"

        # Call the function
        await generate_image_async(self.mock_openai, self.mock_llm, self.story, 0)

        # Verify that the PromptTemplate was created with our template
        mock_prompt_template.assert_called_once()


if __name__ == "__main__":
    unittest.main()
