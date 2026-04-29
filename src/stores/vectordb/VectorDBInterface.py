from abc import ABC, abstractmethod


class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        # Connect to the vector database
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, embedding_size: int):
        # Create a new collection to store vectors in
        pass

    @abstractmethod
    def add_documents(self, collection_name: str, texts: list,
                      vectors: list, metadata: list):
        # Store text chunks and their vectors in the collection
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str,
                         query_vector: list, top_k: int = 5):
        # Find the most similar vectors to the query vector
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        # Delete a collection and all its vectors
        pass

    @abstractmethod
    def is_collection_exists(self, collection_name: str):
        # Check if a collection exists
        pass