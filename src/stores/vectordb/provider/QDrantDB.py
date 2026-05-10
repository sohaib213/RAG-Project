from qdrant_client import QdrantClient
from stores.vectordb.VectorDBInterface import VectorDBInterface
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid
from types import SimpleNamespace
from models.db_schemes import RetrievalDocument


class QDrantDB(VectorDBInterface):

    # more flexibility :)
    distance_map = {
        "Cosine": Distance.COSINE, # meaning dirction lw data not normalized
        "Dot": Distance.DOT, # meaning dirction and magnitude useful lw data normalized
        "Euclid": Distance.EUCLID, #distance
    }

    def __init__(self, url, api_key, distance_metric="Cosine"):
        self.url = url
        self.api_key = api_key
        self.client = None
        # for flexibility :)
        self.distance_metric = distance_metric
        self.connect()

    def connect(self):
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key
        )

    #OG
    def create_collection(self, collection_name: str, embedding_size: int):
        # 3shan mynfash n3ml same collection name twice
        if self.is_collection_exists(collection_name):
            return
        
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=embedding_size,
                
                # distance map lle be chosen by the user but defult value lle used in case of error 
                distance = self.distance_map.get(self.distance_metric, Distance.COSINE)
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
        
    ##########################search##########################

    # for hyprid search might be useful in some cases
    def search_keyword(self, query: str, results: list) -> list:
       return [r.text for r in results if query.lower() in r.text.lower()]



    # applied score threshold to filter out low-relevance results,
    # especially important for small medical datasets to reduce hallucinations.
    def search_by_vector(
        self,
        collection_name: str,
        query_vector: list,
        top_k: int = 5,
        score_threshold: float = 0.2 
    ):
        # check collection
        if not self.is_collection_exists(collection_name):
            return []
        
        #to handle  Qdrant failures :)
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )

        except Exception as e:
            print(f"[ERROR] Qdrant search failed: {e}")
            return []

        # transform safely
        formatted = []
        for r in results:
            payload = r.payload or {}
            text = payload.get("text", "")

            formatted.append(
                RetrievalDocument(
                    text=text,
                    score=r.score
                )
            )

        return formatted