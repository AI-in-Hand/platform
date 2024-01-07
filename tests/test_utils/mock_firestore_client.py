class MockFirestoreClient:
    def __init__(self):
        self._collections = {}
        self.collection_name = "agency_configs"
        self.current_document = None

    def collection(self, collection_name):
        self._collections[collection_name] = self._collections.get(collection_name, {})
        return self

    def document(self, document_name):
        self.current_document = document_name
        return self

    def get(self):
        # Return self to support chaining and access to `exists` and `to_dict`
        return self

    def exists(self):
        collection = self._collections.get(self.collection_name, {})
        return self.current_document in collection

    def set(self, collection_name, document_name, data):
        self._collections.setdefault(collection_name, {})[document_name] = data

    def to_dict(self):
        collection = self._collections.get(self.collection_name, {})
        return collection.get(self.current_document, {})

    # Call this method to setup your mock data in tests
    def setup_mock_data(self, collection_name, document_name, data):
        self.set(collection_name, document_name, data)
