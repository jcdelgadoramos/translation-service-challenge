from pydantic import BaseModel


class Word(BaseModel):
    name: str
    language: str
    definitions: list[str] = []
    synonyms: list[str] = []
    translations: dict[str, str] = {}
    examples: list[str] = []
