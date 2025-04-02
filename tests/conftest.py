"""
Pytest configuration for DeepBook tests.
"""

import pytest

from app.models import (
    BookOutlineModel,
    ChapterOutlineModel,
    ChapterTextModel,
    CharacterModel,
    CharactersModel,
    FullTextModel,
    MetaDataModel,
    Story,
)


@pytest.fixture
def sample_story():
    """Create a sample story for testing."""
    story = Story(prompt="A story about a brave turtle who helps his forest friends")

    # Add metadata
    story.metadata = MetaDataModel(
        title="The Adventures of Timmy",
        author="Wanda Wordsmith",
        year=2023,
        themes=["friendship", "bravery", "animals"],
        location="Whispering Forest",
    )

    # Add characters
    story.characters = CharactersModel(
        characters=[
            CharacterModel(
                name="Timmy",
                description="A small green turtle with a bright yellow shell",
                personality="Timmy is brave but cautious, always helping others despite his fears.",
            ),
            CharacterModel(
                name="Luna",
                description="A wise old owl with silver feathers",
                personality="Luna is knowledgeable and kind, guiding the forest creatures with her wisdom.",
            ),
        ]
    )

    # Add outline
    story.outline = BookOutlineModel(
        synopsis="A story about a brave turtle helping his forest friends during a storm.",
        conflict="The animals of the forest must find shelter before the big storm hits.",
        resolution="Timmy leads everyone to a cave he discovered, saving them from the storm.",
        outlines=[
            ChapterOutlineModel(
                chapter=1,
                title="The Big Storm",
                synopsis="Timmy helps his friends prepare for an unexpected storm.",
            ),
            ChapterOutlineModel(
                chapter=2,
                title="Luna's Wisdom",
                synopsis="Timmy seeks advice from Luna the owl to find shelter.",
            ),
            ChapterOutlineModel(
                chapter=3,
                title="The Hidden Cave",
                synopsis="Timmy remembers a cave he found while exploring and leads everyone there.",
            ),
        ],
    )

    # Add text
    story.text = FullTextModel(
        chapters=[
            ChapterTextModel(
                chapter=1,
                text="The sun was shining brightly over Whispering Forest when Timmy the turtle noticed dark clouds gathering in the distance...",
            ),
            ChapterTextModel(
                chapter=2,
                text='"Luna," called Timmy, "we need your help! A storm is coming and we need a safe place to shelter!"...',
            ),
            ChapterTextModel(
                chapter=3,
                text="Suddenly, Timmy remembered the cave he had discovered last week while exploring the rocky hills...",
            ),
        ]
    )

    return story
