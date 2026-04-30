import os
from src.controllers.BaseController import BaseController


class FileController(BaseController):

    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        # Build the path for this project's folder
        project_path = os.path.join(self.files_dir, project_id)

        # Create the folder if it doesn't exist
        if not os.path.exists(project_path):
            os.makedirs(project_path)

        return project_path

    def get_file_path(self, project_id: str, file_name: str):
        # Get the project folder path first
        project_path = self.get_project_path(project_id)

        # Then return the full path including the file name
        return os.path.join(project_path, file_name)