class MockFirestoreClient:
    def __init__(self):
        self._data = {}
        self.exists = False

    def collection(self, collection_name):  # noqa: ARG002
        return self

    def document(self, document_name):
        # Simulate the existence of the document based on test data
        self.exists = document_name in self._data
        return self

    def get(self):
        # Return self to support chaining and access to `exists` and `to_dict`
        return self

    def set(self, data):
        self._data = data

    def to_dict(self):
        return self._data
