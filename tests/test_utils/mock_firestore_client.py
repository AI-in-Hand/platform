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

    def set(self, collection_name, document_name, data):
        self._collections.setdefault(collection_name, {})[document_name] = data

    def to_dict(self):
        collection = self._collections.get(self.current_collection, {})
        return collection.get(self.current_document, {})

    def setup_mock_data(self, collection_name, document_name, data):
        self.set(collection_name, document_name, data)
