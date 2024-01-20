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
        self.current_collection = None
        self.current_document = None
        self.current_document_id = None

    def collection(self, collection_name):
        self.current_collection = collection_name
        return self

    def document(self, document_name):
        self.current_document = document_name
        return self

    def get(self):
        return self

    @property
    def exists(self):
        collection = self._collections.get(self.current_collection, {})
        return self.current_document in collection

    def set(self, data: dict):
        self._collections.setdefault(self.current_collection, {})[self.current_document] = data

    def to_dict(self):
        collection = self._collections.get(self.current_collection, {})
        return collection.get(self.current_document, {})

    def setup_mock_data(self, collection_name, document_name, data, doc_id=None):
        self.current_collection = collection_name
        self.current_document = document_name
        self.current_document_id = doc_id
        self.set(data)

    def where(self, filter: FieldFilter):
        # Extract field, op, and value from the FieldFilter object
        self._where_field = filter.field_path
        self._where_op = filter.op_string
        self._where_value = filter.value
        return self

    def stream(self):
        # This method should return a list of mock documents
        # matching the criteria set in the 'where' method.
        matching_docs = []
        for doc_id, doc in self._collections.get(self.current_collection, {}).items():
            if doc.get(self._where_field) == self._where_value:
                matching_docs.append(MockDocumentSnapshot(doc_id, doc))
        return matching_docs

    def add(self, data) -> list[MockDocumentSnapshot]:
        # This method should add a new document to the collection
        # and return a list with the new document.
        self.set(data)
        return [MockDocumentSnapshot(self.current_document_id, data)]
