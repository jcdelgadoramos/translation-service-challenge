from unittest import TestCase
from unittest.mock import Mock, patch
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from typing import List

from firestore_client import FirestoreClient
from translate_client import translate
from models import WordModel
from main import app


@patch("firestore_client.Client")
class FirestoreClientTest(TestCase):
    """
    This class contains tests for FirestoreClient
    """

    def setUp(self) -> None:
        self.word = "algo"
        self.other_word = "other"
        self.source_lang = "es"
        self.target_lang = "en"
        self.limit = 2
        self.page = 2
        self.desc = False

    @patch("firestore_client.FieldFilter")
    def test_query_by_name(self, MockFieldFilter, _) -> None:
        client = FirestoreClient(self.source_lang)
        client.query_by_name(self.word)
        client.collection.where.assert_called_once_with(filter=MockFieldFilter())

    @patch("firestore_client.FieldFilter")
    def test_query_filter(self, MockFieldFilter, _) -> None:
        client = FirestoreClient(self.source_lang)
        mock_last_pop = Mock()
        mock_dict = {"name": self.other_word}
        mock_last_pop.to_dict.return_value = mock_dict
        client.collection.where().where().order_by().limit().stream.return_value = [
            Mock(),
            mock_last_pop,
        ]
        client.query_filter(self.word, self.limit, self.page, self.desc)
        client.collection.where().where().order_by().start_after.assert_called_once_with(
            mock_dict
        )

    def test_create_word(self, _) -> None:
        client = FirestoreClient(self.source_lang)
        with patch("firestore_client.WordModel") as MockWordModel:
            client.create_word(MockWordModel())
            client.collection.document.assert_called_once_with(MockWordModel().name)

    def test_delete_word(self, _) -> None:
        client = FirestoreClient(self.source_lang)
        client.delete_word(self.word)
        client.collection.document.assert_called_once()


@patch("translate_client.TranslateClient")
class TranslateClientTest(TestCase):
    """
    This class contains tests for the Google Translate client
    """

    def setUp(self) -> None:
        self.word = "algo"
        self.source_lang = "es"
        self.target_lang = "en"
        self.translated_dict = "some"

    def test_translate(self, MockTranslateClient) -> None:
        MockTranslateClient().translate().__getitem__.return_value = (
            self.translated_dict
        )
        word_instance = translate(self.word, self.source_lang, self.target_lang)
        self.assertEqual(
            self.translated_dict, word_instance.translations[self.target_lang]
        )


class LookupEndpointTest(TestCase):
    """
    This class contains tests for lookup endpoint
    """

    def setUp(self):
        self.client = TestClient(app)
        self.word = "algo"
        self.en_translation = "something"
        self.fr_translation = "quelque chose"
        self.source_lang = "es"
        self.en_target_lang = "en"
        self.fr_target_lang = "fr"
        self.en_word_object = WordModel(
            name=self.word,
            language=self.source_lang,
            translations={self.en_target_lang: self.en_translation},
        )
        self.fr_word_object = WordModel(
            name=self.word,
            language=self.source_lang,
            translations={self.fr_target_lang: self.fr_translation},
        )
        self.two_lang_word_object = WordModel(
            name=self.word,
            language=self.source_lang,
            translations={
                self.en_target_lang: self.en_translation,
                self.fr_target_lang: self.fr_translation,
            },
        )

    @patch("main.FirestoreClient")
    @patch("main.translate")
    def test_new_word(self, mock_translate, MockFirestoreClient):
        """
        This test evaluates if a word has been found in the DB
        """

        mock_translate.return_value = self.en_word_object
        MockFirestoreClient().query_by_name().get.return_value = []
        response = self.client.get(
            f"/lookup/{self.source_lang}/{self.en_target_lang}/{self.word}"
        )
        response_word_object = WordModel(**(response.json()))
        MockFirestoreClient().create_word.assert_called_once_with(self.en_word_object)
        self.assertEqual(self.en_word_object, response_word_object)

    @patch("main.FirestoreClient")
    def test_existing_word_with_translation_in_target_lang(self, MockFirestoreClient):
        """
        This test evaluates if a word has been found in the DB
        No mock is needed for translate function, since it should not be called
        """

        return_word_mock = Mock()
        return_word_mock.to_dict.return_value = dict(self.en_word_object)
        MockFirestoreClient().query_by_name().get.return_value = [
            return_word_mock,
        ]
        response = self.client.get(
            f"/lookup/{self.source_lang}/{self.en_target_lang}/{self.word}"
        )
        response_word_object = WordModel(**(response.json()))
        MockFirestoreClient().create_word.assert_not_called()
        self.assertEqual(self.en_word_object, response_word_object)

    @patch("main.FirestoreClient")
    @patch("main.translate")
    def test_existing_word_with_no_translation_in_target_lang(
        self, mock_translate, MockFirestoreClient
    ):
        """
        This test evaluates if a word has been found in the DB
        """

        mock_translate.return_value = self.fr_word_object
        return_word_mock = Mock()
        return_word_mock.to_dict.return_value = dict(self.en_word_object)
        MockFirestoreClient().query_by_name().get.return_value = [
            return_word_mock,
        ]
        response = self.client.get(
            f"/lookup/{self.source_lang}/{self.fr_target_lang}/{self.word}"
        )
        response_word_object = WordModel(**(response.json()))
        MockFirestoreClient().create_word.assert_called_once_with(
            self.two_lang_word_object
        )
        self.assertEqual(self.fr_word_object, response_word_object)

    @patch("main.FirestoreClient")
    def test_list_custom_params(self, MockFirestoreClient):
        """
        This test evaluates list endpoint, and if params are being passed properly
        """

        limit_param = 5
        page_param = 2
        desc_param = "false"
        desc_value = False
        return_word_mock = Mock()
        return_word_mock.to_dict.return_value = dict(self.two_lang_word_object)
        MockFirestoreClient().query_filter().get.return_value = [
            return_word_mock,
        ]
        response = self.client.get(
            f"/list/{self.source_lang}?word={self.word}"
            f"&limit={limit_param}&page={page_param}&desc={desc_param}"
        )
        response_word_object = TypeAdapter(List[WordModel]).validate_python(
            response.json()
        )
        MockFirestoreClient().query_filter.assert_called_with(
            self.word,
            limit_param,
            page_param,
            desc_value,
        )
        self.assertEqual(
            [
                self.two_lang_word_object,
            ],
            response_word_object,
        )

    @patch("main.FirestoreClient")
    def test_delete(self, MockFirestoreClient):
        """
        Test evaluates delete endpoint, including method
        """

        response = self.client.delete(f"/delete/{self.source_lang}/{self.word}")
        MockFirestoreClient.assert_called_once_with(language=self.source_lang)
        MockFirestoreClient().delete_word.assert_called_once_with(self.word)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        wrong_response = self.client.get(f"/delete/{self.source_lang}/{self.word}")
        self.assertEqual(wrong_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
