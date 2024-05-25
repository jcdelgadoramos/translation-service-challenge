from google.cloud.translate_v2.client import Client as TranslateClient

from models import WordModel


def translate(word: str, source_lang: str, target_lang: str) -> WordModel:
    """
    Connects to Google Translate Client for word translation

    :param str word: Word being translated
    :param str source_lang: Language from which the word is being traslated
    :param str target_lang: Language to which th word is being traslated to

    :return: WordModel object
    """

    gt_client = TranslateClient()
    translated_text = gt_client.translate(
        word, target_language=target_lang, source_language=source_lang
    )
    word_instance = WordModel(name=word, language=source_lang)
    word_instance.translations[target_lang] = translated_text["translatedText"]

    return word_instance
