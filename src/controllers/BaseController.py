import os
from helpers import get_settings


class BaseController:

    def __init__(self):
        self.settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.files_dir = os.path.join(self.base_dir, "assets", "files")
        self.db_dir = os.path.join(self.base_dir, "assets", "db")

    def get_db_path(self, db_name: str):
        # Creates the db folder if it doesn't exist yet and returns the path
        db_path = os.path.join(self.db_dir, db_name)
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        return db_path