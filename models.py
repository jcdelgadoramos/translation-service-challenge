from pydantic import BaseModel


class Word(BaseModel):
    name: str
    definitions: list[str] = []
    synonyms: list[str] = []
    translations: list[str] = []
    examples: list[str] = []
