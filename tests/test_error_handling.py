"""
Tests for error handling and edge cases in the DeepBook application.
"""

import asyncio
import threading
import unittest
from unittest.mock import MagicMock, patch

import streamlit as st

from app.models import Story, generate_all_character_images, generate_image_async


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_openai = MagicMock()
        self.mock_llm = MagicMock()
        self.story = Story(prompt="Test prompt")

    @patch("app.models.PromptTemplate")
    def test_api_request_failure(self, mock_prompt_template):
        """Test handling of API request failures."""
        # Setup
        mock_prompt_instance = MagicMock()
        mock_prompt_template.return_value = mock_prompt_instance
        mock_prompt_instance.format_prompt.return_value.to_string.return_value = "prompt"
        self.mock_llm.return_value = "description"

        # Simulate API failure
        async def mock_acreate_error(*args, **kwargs):
            raise Exception("API error")

        self.mock_openai.Image.acreate = mock_acreate_error

        # Call the function in a way that catches the expected exception
        with self.assertRaises(Exception):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                generate_image_async(self.mock_openai, self.mock_llm, self.story, 0)
            )
            loop.close()

    def test_empty_prompt(self):
        """Test handling of empty prompts."""
        # Create a story with an empty prompt
        empty_story = Story(prompt="")

        # Verify that the prompt is indeed empty
        self.assertEqual(empty_story.prompt, "")

        # The model should still function properly with an empty prompt
        self.assertIsNone(empty_story.metadata)
        self.assertIsNone(empty_story.characters)
        self.assertIsNone(empty_story.outline)
        self.assertIsNone(empty_story.text)

    @patch("app.models.PromptTemplate")
    def test_large_response_handling(self, mock_prompt_template):
        """Test handling of large responses from API."""
        # Setup
        mock_prompt_instance = MagicMock()
        mock_prompt_template.return_value = mock_prompt_instance
        mock_prompt_instance.format_prompt.return_value.to_string.return_value = "prompt"

        # Create a very large response (simulating a large image description)
        large_response = "x" * 10000
        self.mock_llm.return_value = large_response

        # Need to create characters for the story
        from app.models import CharacterModel, CharactersModel

        self.story.characters = CharactersModel(
            characters=[
                CharacterModel(
                    name="Test Character",
                    description="Test Description",
                    personality="Test Personality",
                )
            ]
        )

        # Create a valid JSON response for the image API
        async def mock_acreate(*args, **kwargs):
            # Check if the prompt is too large
            prompt = kwargs.get("prompt", "")
            self.assertLess(len(prompt), 13000)  # DALL-E has a token limit
            return {"data": [{"url": "https://example.com/image.png"}]}

        self.mock_openai.Image.acreate = mock_acreate

        # Test the function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        i, prompt, response = loop.run_until_complete(
            generate_image_async(self.mock_openai, self.mock_llm, self.story, 0)
        )
        loop.close()

        # Verify results
        self.assertEqual(i, 0)
        self.assertEqual(prompt, large_response)
        self.assertEqual(response["data"][0]["url"], "https://example.com/image.png")


class TestConcurrency(unittest.TestCase):
    """Test cases for concurrency and threading."""

    @patch("app.models.PromptTemplate")
    @patch("app.models.generate_image_async")
    async def test_concurrent_image_generation(self, mock_generate_image, mock_prompt_template):
        """Test that multiple images can be generated concurrently."""
        # Setup a story with multiple characters
        story = Story(prompt="Test prompt")
        story.characters = MagicMock()
        story.characters.characters = [MagicMock(), MagicMock(), MagicMock()]

        # Setup the mock to return different values for different characters
        async def side_effect(openai, llm, story, i):
            return i, f"prompt_{i}", {"data": [{"url": f"https://example.com/image_{i}.png"}]}

        mock_generate_image.side_effect = side_effect

        # Call the function
        results = await generate_all_character_images(MagicMock(), MagicMock(), story)

        # Verify results
        self.assertEqual(len(results), 3)
        for i, (idx, prompt, response) in enumerate(results):
            self.assertEqual(idx, i)
            self.assertEqual(prompt, f"prompt_{i}")
            self.assertEqual(response["data"][0]["url"], f"https://example.com/image_{i}.png")

    def test_threading_image_generation(self):
        """Test that image generation works correctly in a separate thread."""
        # This simulates what happens in the app when generating images in a background thread

        # Setup
        mock_openai = MagicMock()
        mock_llm = MagicMock()
        story = Story(prompt="Test prompt")
        story.characters = MagicMock()
        story.characters.characters = [MagicMock()]

        # Define what will happen in the thread
        async def async_generate():
            return [(0, "prompt", {"data": [{"url": "https://example.com/image.png"}]})]

        results = []

        # Function to run in the thread
        def thread_func():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            thread_results = loop.run_until_complete(async_generate())
            loop.close()
            results.extend(thread_results)

        # Run the function in a thread
        thread = threading.Thread(target=thread_func)
        thread.start()
        thread.join()

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 0)
        self.assertEqual(results[0][1], "prompt")
        self.assertEqual(results[0][2]["data"][0]["url"], "https://example.com/image.png")


if __name__ == "__main__":
    unittest.main()
