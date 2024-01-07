class MockFirestoreClient:
    def __init__(self):
        self._collections = {}
        self.current_collection = None
        self.current_document = None

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

    def setup_mock_data(self, collection_name, document_name, data):
        self.current_collection = collection_name
        self.current_document = document_name
        self.set(data)

    def where(self, field, op, value):
        # This is a simplified implementation.
        # Adjust the logic to suit your specific query requirements.
        self._where_field = field
        self._where_op = op
        self._where_value = value
        return self

    def stream(self):
        # This method should return a list of mock documents
        # matching the criteria set in the 'where' method.
        matching_docs = []
        for doc_id, doc in self._collections.get(self.current_collection, {}).items():
            if doc.get(self._where_field) == self._where_value:
                matching_docs.append(MockDocumentSnapshot(doc_id, doc))
        return matching_docs


class MockDocumentSnapshot:
    def __init__(self, id, data):
        self.id = id
        self._data = data

    def to_dict(self):
        return self._data
