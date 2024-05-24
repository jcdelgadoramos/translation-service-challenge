from google.cloud.translate_v2.client import Client

from models import Word


def translate(word: str, source_lang: str, target_lang: str) -> Word:
    # NoSQL logic for translation

    client = Client()
    translated_text = client.translate(word, target_language=target_lang, source_language=source_lang)
    word = Word(name=word, language=source_lang)
    word.translations[target_lang] = translated_text["translatedText"]

    return word
