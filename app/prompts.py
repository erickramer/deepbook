TEMPLATE = """
We're imaginging a new children's story together. We're going to fill in
the details of the story piece-by-piece. Our current story is described by 
the following JSON. 

{story}

Now, we are going to add in the `{name}` field. 

{instructions}    
"""

TEXT_TEMPLATE="""
We're imaginging a new children's story together. We're going to fill in
the details of the story piece-by-piece. Our current story is described by 
the following JSON. 

{story}

Now, we are going to imaging the text for chapter {name}. Please follow
the synposis in the outline for chapter {name} described above.

{instructions}
"""

IMG_TEMPLATE="""
We're imaginging a new children's story together. We're going to fill in
the details of the story piece-by-piece. Our current story is described by 
the following JSON. 

{story}

Please write a prompt for image generation for character {i} based on their
physical description and personality. 

Again this character is described by the following JSON:

{character}
"""