"""
Tests for the Layout class in the DeepBook application.
"""

import unittest
from unittest.mock import MagicMock, patch, call
import streamlit as st
from app import Layout
from app.models import Story, MetaDataModel, CharacterModel, CharactersModel
from app.models import ChapterOutlineModel, BookOutlineModel, ChapterTextModel, FullTextModel


class TestLayout(unittest.TestCase):
    """Test cases for the Layout class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects for streamlit components
        self.mock_container = MagicMock()
        self.mock_column = MagicMock()
        
        # Patch streamlit's container method
        patcher = patch.object(st, 'container', return_value=self.mock_container)
        self.addCleanup(patcher.stop)
        self.mock_st_container = patcher.start()
        
        # Patch the columns method of containers
        patcher = patch.object(self.mock_container, 'columns', return_value=[self.mock_column, self.mock_column])
        self.addCleanup(patcher.stop)
        self.mock_columns = patcher.start()
        
        # Create a layout instance
        self.layout = Layout()
        
        # Create a test story
        self.story = Story(prompt="A test story")
        self.story.metadata = MetaDataModel(
            title="Test Title",
            author="Test Author",
            year=2023,
            themes=["test"],
            location="Test Location"
        )
        
        # Add characters to the story
        self.story.characters = CharactersModel(characters=[
            CharacterModel(
                name="Character 1",
                description="Description 1",
                personality="Personality 1"
            ),
            CharacterModel(
                name="Character 2",
                description="Description 2",
                personality="Personality 2"
            )
        ])
        
        # Add outline to the story
        self.story.outline = BookOutlineModel(
            synopsis="Test synopsis",
            conflict="Test conflict",
            resolution="Test resolution",
            outlines=[
                ChapterOutlineModel(
                    chapter=1,
                    title="Chapter 1",
                    synopsis="Synopsis 1"
                ),
                ChapterOutlineModel(
                    chapter=2,
                    title="Chapter 2",
                    synopsis="Synopsis 2"
                )
            ]
        )
        
        # Add text to the story
        self.story.text = FullTextModel(chapters=[
            ChapterTextModel(
                chapter=1,
                text="Chapter 1 text"
            ),
            ChapterTextModel(
                chapter=2,
                text="Chapter 2 text"
            )
        ])
    
    def test_init(self):
        """Test that Layout initialization creates all necessary containers."""
        # Verify that containers were created
        self.assertEqual(self.mock_st_container.call_count, 5)  # header, characters, outline, text, appendix
        
        # Verify that section headers were written
        self.mock_container.write.assert_has_calls([
            call("## Starring"),
            call("## Contents"),
            call("## Story"),
            call("## Logs")
        ], any_order=True)
    
    def test_add_log(self):
        """Test adding logs to the appendix section."""
        self.layout.add_log(self.story)
        
        # Verify that the appendix container's write and code methods were called
        self.mock_container.write.assert_any_call("\n")
        self.mock_container.code.assert_called_once()
    
    def test_add_metadata(self):
        """Test adding metadata to the header section."""
        self.layout.add_log = MagicMock()  # Mock the add_log method
        
        self.layout.add_metadata(self.story)
        
        # Verify that the header container's write method was called with the title and author
        self.mock_container.write.assert_has_calls([
            call("# Test Title"),
            call("By Test Author")
        ])
        
        # Verify that add_log was called
        self.layout.add_log.assert_called_once_with(self.story)
    
    def test_add_characters(self):
        """Test adding characters to the characters section."""
        # Mock the add_character and add_log methods
        self.layout.add_character = MagicMock()
        self.layout.add_log = MagicMock()
        
        # Setup container for character containers
        self.layout.characters.container = MagicMock(return_value=MagicMock())
        
        self.layout.add_characters(self.story)
        
        # Verify that add_character was called for each character
        self.layout.add_character.assert_has_calls([
            call(0, self.story.characters.characters[0]),
            call(1, self.story.characters.characters[1])
        ])
        
        # Verify that add_log was called
        self.layout.add_log.assert_called_once_with(self.story)
    
    def test_add_outline(self):
        """Test adding outline to the contents section."""
        self.layout.add_log = MagicMock()  # Mock the add_log method
        
        self.layout.add_outline(self.story)
        
        # Verify that the outline container's write method was called for each chapter outline
        self.mock_container.write.assert_has_calls([
            call("**Chapter 1**: Chapter 1"),
            call("**Chapter 2**: Chapter 2")
        ])
        
        # Verify that add_log was called
        self.layout.add_log.assert_called_once_with(self.story)
    
    def test_add_text(self):
        """Test adding text to the story section."""
        self.layout.add_log = MagicMock()  # Mock the add_log method
        
        self.layout.add_text(self.story)
        
        # Verify that the text container's write method was called for each chapter
        self.mock_container.write.assert_has_calls([
            call("### Chapter 1: Chapter 1"),
            call("Chapter 1 text"),
            call("### Chapter 2: Chapter 2"),
            call("Chapter 2 text")
        ])
        
        # Verify that add_log was called for each chapter
        self.assertEqual(self.layout.add_log.call_count, 2)
    
    def test_add_character_img(self):
        """Test adding character images."""
        # Setup the character_img_cols list
        self.layout.character_img_cols = [self.mock_column, self.mock_column]
        
        self.layout.add_character_img(0, "https://example.com/image.png")
        
        # Verify that the column's image method was called with the URL
        self.mock_column.image.assert_called_once_with("https://example.com/image.png")


if __name__ == '__main__':
    unittest.main()