"""
Tests for the prompt templates in the DeepBook application.
"""

import unittest
from app.prompts import TEMPLATE, TEXT_TEMPLATE, IMG_TEMPLATE


class TestPrompts(unittest.TestCase):
    """Test cases for the prompt templates."""
    
    def test_template_format(self):
        """Test that the main template can be formatted correctly."""
        story_json = '{"prompt": "test prompt"}'
        name = "metadata"
        instructions = "Follow these instructions"
        
        # Format the template
        formatted = TEMPLATE.format(
            story=story_json,
            name=name,
            instructions=instructions
        )
        
        # Check that all placeholders were replaced
        self.assertIn(story_json, formatted)
        self.assertIn(name, formatted)
        self.assertIn(instructions, formatted)
        self.assertNotIn("{story}", formatted)
        self.assertNotIn("{name}", formatted)
        self.assertNotIn("{instructions}", formatted)
    
    def test_text_template_format(self):
        """Test that the text template can be formatted correctly."""
        story_json = '{"prompt": "test prompt"}'
        name = "1"
        instructions = "Follow these instructions"
        
        # Format the template
        formatted = TEXT_TEMPLATE.format(
            story=story_json,
            name=name,
            instructions=instructions
        )
        
        # Check that all placeholders were replaced
        self.assertIn(story_json, formatted)
        self.assertIn(name, formatted)
        self.assertIn(instructions, formatted)
        self.assertNotIn("{story}", formatted)
        self.assertNotIn("{name}", formatted)
        self.assertNotIn("{instructions}", formatted)
    
    def test_img_template_format(self):
        """Test that the image template can be formatted correctly."""
        story_json = '{"prompt": "test prompt"}'
        i = "0"
        character = '{"name": "Test Character"}'
        
        # Format the template
        formatted = IMG_TEMPLATE.format(
            story=story_json,
            i=i,
            character=character
        )
        
        # Check that all placeholders were replaced
        self.assertIn(story_json, formatted)
        self.assertIn(i, formatted)
        self.assertIn(character, formatted)
        self.assertNotIn("{story}", formatted)
        self.assertNotIn("{i}", formatted)
        self.assertNotIn("{character}", formatted)
    
    def test_template_content(self):
        """Test that templates contain expected guidance text."""
        # Main template
        self.assertIn("We're imagining a new children's story together", TEMPLATE)
        self.assertIn("add in the `{name}` field", TEMPLATE)
        
        # Text template
        self.assertIn("imagine the text for chapter {name}", TEXT_TEMPLATE)
        self.assertIn("follow the synopsis in the outline", TEXT_TEMPLATE)
        
        # Image template
        self.assertIn("write a prompt for image generation for character {i}", IMG_TEMPLATE)
        self.assertIn("based on their physical description and personality", IMG_TEMPLATE)


if __name__ == '__main__':
    unittest.main()