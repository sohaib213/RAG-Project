from qdrant_client import QdrantClient
from stores.vectordb.VectorDBInterface import VectorDBInterface
#OG
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid
from types import SimpleNamespace

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

    #OG
    def create_collection(self, collection_name: str, embedding_size: int):
        # Member 2 will implement this
        if self.is_collection_exists(collection_name):
            return
        
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=embedding_size,
                distance=Distance.COSINE
            )
        )

    #OG
    def add_documents(self, collection_name: str, texts: list, vectors: list, metadata: list):
        # Member 2 will implement this
        points = []

        for text, vector, meta in zip(texts, vectors, metadata):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": text,
                        "metadata": meta
                    }
                )
            )

        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    #OG
    def search_by_vector(self, collection_name: str, query_vector: list, top_k: int = 5):
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )

        # Transformation Layer: Convert ScoredPoint to an object with a .text attribute
        formatted_results = []

        for res in results:
            payload = res.payload or {}

            formatted_results.append(
                SimpleNamespace(
                    text=payload.get("text", ""),
                    metadata=payload.get("metadata", {}),
                    score=res.score
                )
            )

        return formatted_results

    #OG
    def delete_collection(self, collection_name: str):
        # Member 2 will implement this
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            print(f"[WARN] delete_collection failed: {e}")

    #OG
    def is_collection_exists(self, collection_name: str):
        # Member 2 will implement this 
        try:
            return collection_name in [
                c.name for c in self.client.get_collections().collections
            ]
        except Exception:
            return False
