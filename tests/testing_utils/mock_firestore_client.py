from google.cloud.firestore_v1 import FieldFilter


class MockDocumentSnapshot:
    def __init__(self, id, data):
        self.id = id
        self._data = data

    def to_dict(self):
        return self._data


class MockFirestoreClient:
    def __init__(self):
        self._collections = {}
        self._current_collection = None
        self._current_documents = {}

    def collection(self, collection_name):
        self._current_collection = collection_name
        self._collections.setdefault(collection_name, {})
        self._current_documents.setdefault(collection_name, {"current_document": None})
        return self

    def document(self, document_name):
        if self._current_collection:
            self._current_documents[self._current_collection]["current_document"] = document_name
        return self

    def get(self):
        return self

    @property
    def exists(self):
        collection = self._collections.get(self._current_collection, {})
        current_doc = self._current_documents.get(self._current_collection, {}).get("current_document")
        return current_doc in collection

    def set(self, data: dict):
        collection = self._current_collection
        current_doc = self._current_documents[collection]["current_document"]
        self._collections.setdefault(collection, {})[current_doc] = data

    def to_dict(self):
        collection = self._collections.get(self._current_collection, {})
        current_doc = self._current_documents.get(self._current_collection, {}).get("current_document")
        return collection.get(current_doc, {})

    def setup_mock_data(self, collection_name, document_name, data):
        self._current_collection = collection_name
        self._current_documents.setdefault(collection_name, {"current_document": document_name})
        self.set(data)

    def where(self, filter: FieldFilter):
        self._where_field = filter.field_path
        self._where_op = filter.op_string
        self._where_value = filter.value
        return self

    def stream(self):
        matching_docs = []
        collection = self._collections.get(self._current_collection, {})
        for doc_id, doc in collection.items():
            doc_value = doc.get(self._where_field)
            if self._where_op == "in":
                if doc_value in self._where_value:
                    matching_docs.append(MockDocumentSnapshot(doc_id, doc))
            elif self._where_op == "==" and doc_value == self._where_value:
                matching_docs.append(MockDocumentSnapshot(doc_id, doc))
        return iter(matching_docs)

    def add(self, data) -> tuple:
        collection = self._current_collection
        current_doc_id = self._current_documents[collection].get("current_document")
        self.set(data)
        return "timestamp", MockDocumentSnapshot(current_doc_id, data)

    def update(self, data: dict, option=None):  # noqa: ARG002
        collection = self._current_collection
        current_doc_id = self._current_documents[collection].get("current_document")
        current_data = self._collections[collection].get(current_doc_id, {})
        current_data.update(data)
        self._collections[collection][current_doc_id] = current_data

    def delete(self):
        collection = self._current_collection
        current_doc_id = self._current_documents[collection].get("current_document")
        self._collections[collection].pop(current_doc_id, None)
        self._current_documents[collection]["current_document"] = None
