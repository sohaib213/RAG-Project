from controllers.BaseController import BaseController
from stores.vectordb.provider.QDrantDB import QDrantDB


class VectorDBFactory:

    def __init__(self):
        self.base_controller = BaseController()

    def create_client(self, provider: str = "qdrant"):
        if provider == "qdrant":
            db_path = self.base_controller.get_db_path("qdrant_data")
            return QDrantDB(db_path=db_path)

        raise ValueError(f"Unknown vector DB provider: {provider}")