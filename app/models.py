from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import List, Optional
from prompts import TEMPLATE, TEXT_TEMPLATE, IMG_TEMPLATE

class Model(BaseModel):
    pass

class MetaDataModel(Model):
    title: str = Field(description="the title of the children's book",)
    author: str = Field(description="the whimsical and fantasical name for the author")
    year: int = Field(description="the year the book was published in the past or future!")
    themes: List[str] = Field(description="themes touched upon by the book")
    location: str = Field(description="the place where the majority of the story takes place")

class ChapterOutlineModel(Model):
    chapter: int = Field(description="The number of the chapter")
    title: str = Field(description="The title of the chapter")
    synopsis: str = Field(description="1-2 sentence summary of the chapter")

class BookOutlineModel(Model):
    synopsis: str = Field(description="1-2 sentence summary of the book")
    conflict: str = Field(description="The specific conflict that must be resolved or obstacle that must be overcome")
    resolution: str = Field(description="The specific way the conflict is resolved (who, how and when)")
    outlines: List[ChapterOutlineModel] = Field(description="List of outlines for individual chapters")

class CharacterModel(Model):
    name: str = Field(description="name of the character")
    description: str = Field(description="physical description of the character")
    personality: str = Field(description="a one sentence biography of the character")

class CharactersModel(Model):
    characters: List[CharacterModel]

class ChapterTextModel(Model):
    chapter: int = Field("")
    text: str = Field("The text for the chapter. This is the text that is read to children. It should read like a children's book and follow the synopsis in the outline")

class FullTextModel(Model):
    chapters: List[ChapterTextModel] = []

class Story(Model):
    prompt: str = Field(description="A human entered prompt to start the story generation")
    metadata: Optional[MetaDataModel]
    characters: Optional[CharactersModel]
    outline: Optional[BookOutlineModel]
    text: Optional[FullTextModel]

    def _run_llm(self, llm, model: type[Model], name, template=TEMPLATE):
        parser = PydanticOutputParser(pydantic_object=model)
        prompt = PromptTemplate(
            template=template, 
            input_variables=["story"], 
            partial_variables={
                "instructions": parser.get_format_instructions(), 
                "name": name
            }
        )
        output = llm(prompt.format_prompt(story=self.json()).to_string())
        return parser.parse(output)


    def add_metadata(self, llm):        
        self.metadata = self._run_llm(llm, MetaDataModel, "metadata")
        return self

    def add_characters(self,llm):
        self.characters = self._run_llm(llm, CharactersModel, "characters")
        return self

    def add_outline(self,llm):
        self.outline = self._run_llm(llm, BookOutlineModel, "outline")
        return self

    def add_text(self, llm):
        self.text = FullTextModel()

        for outline in self.outline.outlines:
            res = self._run_llm(llm, ChapterTextModel, outline.chapter, TEXT_TEMPLATE)
            self.text.chapters.append(res)

        return self


def generate_image(openai, llm, story: Story, i: int):

    prompt = PromptTemplate(
            template=IMG_TEMPLATE, 
            input_variables=["story", "i", "character"], 
    )

    s = prompt.format_prompt(story=story.json(), i=i, character=story.characters.characters[i]).to_string()
    res = llm(s)

    response = openai.Image.create(
        prompt=f"A children's book illustration. {res}",
        n=1,
        size="512x512"
    )

    return res, response