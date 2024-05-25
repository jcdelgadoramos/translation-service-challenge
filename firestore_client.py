from google.cloud.firestore import Client, CollectionReference, FieldFilter, Query

from models import WordModel


class FirestoreClient:
    db: Client
    collection: CollectionReference

    def __init__(self, language: str) -> None:
        self.db = Client(database="translation-service-challenge-db")
        self.collection = self.db.collection(language)

    def query_by_name(self, word: str) -> Query:
        query = self.collection.where(filter=FieldFilter("name", "==", word))

        return query

    def query_filter(self, word: str, limit: int, page: int, desc: bool) -> Query:
        query_direction = Query.DESCENDING if not desc else Query.ASCENDING
        query = (
            self.collection.where(filter=FieldFilter("name", ">=", word))
            .where(filter=FieldFilter("name", "<=", word + "\uf8ff"))
            .order_by("name", query_direction)
            .limit(limit)
        )
        while page > 1:
            docs = query.stream()
            last_doc = list(docs)[-1]
            last_pop = last_doc.to_dict()["name"]
            query = (
                self.collection.where(filter=FieldFilter("name", ">=", word))
                .where(filter=FieldFilter("name", "<=", word + "\uf8ff"))
                .order_by("name", query_direction)
                .start_after({"name": last_pop})
                .limit(limit)
            )
            page -= 1

        return query

    def create_word(self, word_instance: WordModel) -> None:
        word_document = self.collection.document(word_instance.name)
        word_document.set(word_instance.model_dump())

    def delete_word(self, word: str) -> None:
        self.collection.document(word).delete()
