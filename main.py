from fastapi import FastAPI, status

from firestore_client import FirestoreClient
from models import WordModel
from translate_client import translate

app = FastAPI()


@app.get("/lookup/{source_lang}/{target_lang}/{word}", response_model=WordModel)
async def lookup(source_lang: str, target_lang: str, word: str) -> WordModel:
    """
    This endpoint allows the user to lookup translations
    inside the Firestore DB. If not found, it will retrieve them
    from Google Translate and add them to said DB.

    :param str source_lang: Two-letter language code in which the word
        being evaluated is written, e.g. 'es', 'en'
    :param str target_lang: Two-letter language code to which the word
        is being translated, e.g. 'es', 'en'
    :param str word: Actual word being translated

    :return: WordModel instance containing translation in target language
    """

    firestore_client = FirestoreClient(language=source_lang)
    query = firestore_client.query_by_name(word=word)
    results = query.get()

    if not len(results):
        word_instance = translate(word, source_lang, target_lang)
        firestore_client.create_word(word_instance)
        return word_instance

    word_instance = WordModel(**(results[0].to_dict()))
    if target_lang in word_instance.translations:
        word_instance.translations = {
            target_lang: word_instance.translations[target_lang]
        }
        return word_instance

    new_lang_word_instance = translate(word, source_lang, target_lang)
    word_instance.translations[target_lang] = new_lang_word_instance.translations[
        target_lang
    ]
    firestore_client.create_word(word_instance)

    return new_lang_word_instance


@app.get("/list/{language}/", response_model=list[WordModel])
async def list(
    language: str,
    word: str | None = "",
    limit: int | None = 10,
    page: int | None = 1,
    desc: bool | None = True,
) -> list[WordModel]:
    """
    This endpoint lists the words that match the word being included in the query, as
    well as the language in which the list will be queried.

    :param str language: Two-letter language code from which the stored words will be listed
    :param str word: Optional query param, filters words which match it as substring
    :param int limit: Optional query param, limits result number per request. Default is 10
    :param int page: Optional query param, allows for paginated results when they are
        more than the limit indicated. Default is 1
    :param bool desc: Optional query param, allows ordering results by ascending | descending
        order or words. Default is True

    :return: WordModel list, may be empty depending on data stored in DB
    """

    firestore_client = FirestoreClient(language=language)
    query = firestore_client.query_filter(word, limit, page, desc)

    return [WordModel(**(q.to_dict())) for q in query.get()]


@app.delete("/delete/{language}/{word}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(language: str, word: str):
    """
    This endpoint allows for removal of words in the DB.

    :param str language: Two-letter language code from which the word will be removed if found
    :param str word: Word that will be removed if found
    """

    FirestoreClient(language=language).delete_word(word)
