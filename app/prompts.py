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

Please write a prompt for image generation for character {i} based on their
physical description and personality. 

Again this character is described by the following JSON:

{character}
"""