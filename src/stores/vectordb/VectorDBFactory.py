from helpers import get_settings
from stores.vectordb.provider.QDrantDB import QDrantDB


class VectorDBFactory:

    def __init__(self):
        self.settings = get_settings()

    def create_client(self, provider: str = "qdrant"):
        if provider == "qdrant":
            return QDrantDB(
                url=self.settings.QDRANT_URL,
                api_key=self.settings.QDRANT_API_KEY
            )

        raise ValueError(f"Unknown vector DB provider: {provider}")