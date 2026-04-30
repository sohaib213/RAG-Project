from src.helpers import get_settings


class DataBaseModel:

    def __init__(self, db_client):
        self.db_client = db_client
        self.settings = get_settings()