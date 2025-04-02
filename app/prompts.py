"""
Prompt templates used for generating different parts of the children's storybook.
"""

# Template for generating metadata, characters, and outline
TEMPLATE = """
We're imagining a new children's story together. We're going to fill in
the details of the story piece-by-piece. Our current story is described by
the following JSON.

{story}

Now, we are going to add in the `{name}` field.

{instructions}
"""

# Template for generating chapter text
TEXT_TEMPLATE = """
We're imagining a new children's story together. We're going to fill in
the details of the story piece-by-piece. Our current story is described by
the following JSON.

{story}

Now, we are going to imagine the text for chapter {name}. Please follow
the synopsis in the outline for chapter {name} described above.

{instructions}
"""

# Template for generating character image prompts
IMG_TEMPLATE = """
We're imagining a new children's story together. We're going to fill in
the details of the story piece-by-piece. Our current story is described by
the following JSON.

{story}

Please write a detailed visual description for character {i} that will be used for image generation.
I need you to create a rich, detailed description that includes:

1. Their physical appearance (body shape, size, species if not human)
2. Their facial features and expression
3. Their clothing and accessories
4. Their pose or action they might be doing
5. Any key background elements that represent their world
6. The mood and atmosphere of the image

Make this description vivid and specific, mentioning colors, textures, and small details.
Do not include any disclaimers, explanations, or notes about the image generation process.
Only provide the descriptive prompt itself.

Again this character is described by the following JSON:

{character}
"""
