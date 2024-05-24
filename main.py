from fastapi import FastAPI, status

from models import Word
from translate_client import translate

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/lookup/{source_lang}/{target_lang}/{word}", response_model=Word)
async def lookup(source_lang: str, target_lang: str, word: str):
    # Perform word lookup
    # Should support lookup in NoSQL database before performing
    # lookup in Translate API and storing in NoSQL db if not found
    # If not found anywhere, 

    return translate(word, source_lang, target_lang)

@app.get("/{language}/list", response_model=list[Word])
async def list(language: str):
    # Return list of every word stored in NoSQL db
    # Should support pagination, sorting and filtering
    # Should not return definitions, synonyms and translations unless requested
    # Since nothing is mentioned about returning examples, they will be treated
    # the same as definitions, synonyms and translations

    return [
        Word(
            name="first_word",
            language="en",
            # "definition": "definition",
            # "synonyms": ["list", "of", "synonyms"],
            # "translations": {"es": "Spanish translation", "en": "English translation"},
            # "translations": ["list", "of", "translations"],
            # "examples": ["list", "of", "examples"],
        ),
        Word( 
            name="second_word",
            language="en",
            # "definition": "definition",
            # "synonyms": ["list", "of", "synonyms"],
            # "translations": {"es": "Spanish translation", "en": "English translation"},
            # "examples": ["list", "of", "examples"],
        ),
    ]

@app.delete("/delete/{language}/{word}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(language: str, word: str):
    # Perform word deletion from NoSQL db
    # Should not return anything more than a 204 response

    pass
