from fastapi import FastAPI, status

from firestore_client import FirestoreClient
from models import WordModel
from translate_client import translate

app = FastAPI()


@app.get("/lookup/{source_lang}/{target_lang}/{word}", response_model=WordModel)
async def lookup(source_lang: str, target_lang: str, word: str):
    firestore_client = FirestoreClient(language=source_lang)
    query = firestore_client.query_by_name(word=word)
    results = query.get()

    if not len(results):
        word_instance = translate(word, source_lang, target_lang)
        firestore_client.create_word(word_instance)
        return word_instance

    word_instance = WordModel(**(results[0].to_dict()))
    if target_lang in word_instance.translations:
        word_instance.translations = {target_lang: word_instance.translations[target_lang]}
        return word_instance 
    
    new_lang_word_instance = translate(word, source_lang, target_lang)
    word_instance.translations[target_lang] = new_lang_word_instance.translations[target_lang]
    firestore_client.create_word(word_instance)
    
    return new_lang_word_instance

@app.get("/list/{language}/", response_model=list[WordModel])
async def list(language: str, word: str, limit: int | None = 10, page: int | None = 1, desc: bool | None = True) -> list[WordModel]:
    firestore_client = FirestoreClient(language=language)
    query = firestore_client.query_filter(word, limit, page, desc)

    return [WordModel(**(q.to_dict())) for q in query.get()]

@app.delete("/delete/{language}/{word}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(language: str, word: str):
    FirestoreClient(language=language).delete_word(word)
