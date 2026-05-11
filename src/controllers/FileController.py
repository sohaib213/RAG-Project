import os
from controllers.BaseController import BaseController


class FileController(BaseController):

    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        project_path = os.path.join(self.files_dir, project_id)

        if not os.path.exists(project_path):
            os.makedirs(project_path)

        return project_path

    def get_file_path(self, project_id: str, file_name: str):
        project_path = self.get_project_path(project_id)

        return os.path.join(project_path, file_name)