from qdrant_client import QdrantClient
from stores.vectordb.VectorDBInterface import VectorDBInterface


class QDrantDB(VectorDBInterface):

    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.client = None

    def connect(self):
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key
        )

    def create_collection(self, collection_name: str, embedding_size: int):
        # Member 2 will implement this
        pass

    def add_documents(self, collection_name: str, texts: list,
                      vectors: list, metadata: list):
        # Member 2 will implement this
        pass

    def search_by_vector(self, collection_name: str,
                         query_vector: list, top_k: int = 5):
        # Member 2 will implement this
        pass

    def delete_collection(self, collection_name: str):
        # Member 2 will implement this
        pass

    def is_collection_exists(self, collection_name: str):
        # Member 2 will implement this
        pass