import os
from controllers.BaseController import BaseController
from controllers.FileController import FileController
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader


class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.file_controller = FileController()

    def get_file_loader(self, file_name: str):
        # Get the full path of the file
        file_path = self.file_controller.get_file_path(self.project_id, file_name)

        # Pick the right loader based on the file extension
        extension = os.path.splitext(file_name)[-1].lower()

        if extension == ".txt":
            return TextLoader(file_path, encoding="utf-8")

        if extension == ".pdf":
            return PyMuPDFLoader(file_path)

        # If the extension is not supported, return None
        return None

    def get_file_content(self, file_name: str):
        # Get the correct loader for this file
        loader = self.get_file_loader(file_name)

        if loader is None:
            return None

        # Load and return the file content as a list of documents
        return loader.load()

    def process_file(self, file_name: str, chunk_size: int = 500, overlap: int = 50):
        # First load the file content
        content = self.get_file_content(file_name)

        if content is None:
            return None

        # Set up the splitter with the given chunk size and overlap
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len
        )

        # Split the content into chunks and return them
        chunks = splitter.split_documents(content)
        return chunks