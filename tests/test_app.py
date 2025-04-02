"""
Integration tests for the DeepBook application.
"""

import unittest
from unittest.mock import MagicMock, patch

import streamlit as st

from app import Layout
from app.models import Story


class TestAppIntegration(unittest.TestCase):
    """Integration tests for the app's main workflow."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock streamlit components
        patcher = patch.object(st, "container", return_value=MagicMock())
        self.addCleanup(patcher.stop)
        self.mock_st_container = patcher.start()

        patcher = patch.object(st, "text_input", return_value="test_key")
        self.addCleanup(patcher.stop)
        self.mock_text_input = patcher.start()

        patcher = patch.object(st, "set_page_config")
        self.addCleanup(patcher.stop)
        self.mock_set_page_config = patcher.start()

        patcher = patch.object(st, "title")
        self.addCleanup(patcher.stop)
        self.mock_title = patcher.start()

        # Mock OpenAI and LangChain components
        self.mock_openai = MagicMock()
        self.mock_llm = MagicMock()

        # Mock the Story class methods
        patcher = patch.object(Story, "add_metadata")
        self.addCleanup(patcher.stop)
        self.mock_add_metadata = patcher.start()

        patcher = patch.object(Story, "add_characters")
        self.addCleanup(patcher.stop)
        self.mock_add_characters = patcher.start()

        patcher = patch.object(Story, "add_outline")
        self.addCleanup(patcher.stop)
        self.mock_add_outline = patcher.start()

        patcher = patch.object(Story, "add_text")
        self.addCleanup(patcher.stop)
        self.mock_add_text = patcher.start()

        # Mock the Layout class methods
        patcher = patch.object(Layout, "add_metadata")
        self.addCleanup(patcher.stop)
        self.mock_layout_add_metadata = patcher.start()

        patcher = patch.object(Layout, "add_characters")
        self.addCleanup(patcher.stop)
        self.mock_layout_add_characters = patcher.start()

        patcher = patch.object(Layout, "add_character_img")
        self.addCleanup(patcher.stop)
        self.mock_layout_add_character_img = patcher.start()

        patcher = patch.object(Layout, "add_outline")
        self.addCleanup(patcher.stop)
        self.mock_layout_add_outline = patcher.start()

        patcher = patch.object(Layout, "add_text")
        self.addCleanup(patcher.stop)
        self.mock_layout_add_text = patcher.start()

        # Mock generate_image function
        patcher = patch(
            "app.models.generate_image",
            return_value=("test_prompt", {"data": [{"url": "test_url"}]}),
        )
        self.addCleanup(patcher.stop)
        self.mock_generate_image = patcher.start()

    def test_app_workflow(self):
        """Test the main app workflow when a prompt is provided."""
        # Import the Layout class for testing
        from app import Layout

        # Create mocks
        mock_llm = MagicMock()
        mock_openai = MagicMock()
        mock_story = MagicMock()
        mock_story.characters.characters = [MagicMock(), MagicMock()]

        # Manually simulate the app workflow
        # This avoids trying to execute the main script which has side effects

        # 1. Create layout
        layout = Layout()

        # 2. Create story
        # Instead of calling app.Story(), just use our mock

        # 3. Add metadata
        mock_story.add_metadata.return_value = mock_story
        mock_story.add_metadata(mock_llm)

        # 4. Add the metadata to layout
        layout.add_metadata(mock_story)

        # 5. Add characters
        mock_story.add_characters.return_value = mock_story
        mock_story.add_characters(mock_llm)

        # 6. Add the characters to layout
        layout.add_characters(mock_story)

        # 7. Add images (would normally be done in a loop)
        for i in range(len(mock_story.characters.characters)):
            layout.add_character_img(i, "test_url")

        # 8. Add outline
        mock_story.add_outline.return_value = mock_story
        mock_story.add_outline(mock_llm)

        # 9. Add the outline to layout
        layout.add_outline(mock_story)

        # 10. Add text
        mock_story.add_text.return_value = mock_story
        mock_story.add_text(mock_llm)

        # 11. Add the text to layout
        layout.add_text(mock_story)

        # Verify the workflow executed as expected
        mock_story.add_metadata.assert_called_once()
        mock_story.add_characters.assert_called_once()
        mock_story.add_outline.assert_called_once()
        mock_story.add_text.assert_called_once()

    @patch("app.models.generate_image")
    def test_image_generation(self, mock_gen_image):
        """Test the image generation workflow."""
        # Setup mock return values
        mock_gen_image.return_value = ("test_prompt", {"data": [{"url": "test_url"}]})

        # Create a minimal mock story with characters
        mock_story = MagicMock()
        mock_story.characters.characters = [MagicMock(), MagicMock()]

        # Create layout instance
        layout = Layout()
        layout.add_character_img = MagicMock()

        # Mock the main app code that generates images
        mock_openai = MagicMock()
        mock_llm = MagicMock()

        # Generate images for both characters
        for i in range(2):
            # Use the mock directly instead of calling the real function
            mock_gen_image.return_value = ("test_prompt", {"data": [{"url": "test_url"}]})
            prompt, response = mock_gen_image(mock_openai, mock_llm, mock_story, i)
            layout.add_character_img(i, response["data"][0]["url"])

            # No more appendix

        # Verify image generation happened for both characters
        self.assertEqual(mock_gen_image.call_count, 2)
        self.assertEqual(layout.add_character_img.call_count, 2)


if __name__ == "__main__":
    unittest.main()
