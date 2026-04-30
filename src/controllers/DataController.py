from fastapi import UploadFile
from src.helpers import get_settings


class DataController:

    def __init__(self):
        self.settings = get_settings()

    def validate_file(self, file: UploadFile):
        # Check if the file type is in our allowed list
        if file.content_type not in self.settings.FILE_ALLOWED_EXTENSIONS:
            return False, "File type not allowed"

        # Check if the file size exceeds the limit
        if file.size > self.settings.FILE_MAX_SIZE_MB * 1024 * 1024:
            return False, "File size exceeds the allowed limit"

        return True, "File is valid"