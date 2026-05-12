import os
import re
from controllers.BaseController import BaseController
from controllers.FileController import FileController
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader


class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.file_controller = FileController()

    def get_file_loader(self, file_name: str):
        file_path = self.file_controller.get_file_path(self.project_id, file_name)

        extension = os.path.splitext(file_name)[-1].lower()

        if extension == ".txt":
            return TextLoader(file_path, encoding="utf-8")

        if extension == ".pdf":
            return PyMuPDFLoader(file_path)

        return None

    def get_file_content(self, file_name: str):
        loader = self.get_file_loader(file_name)

        if loader is None:
            return None

        return loader.load()

    def clean_text(self, documents):
        cleaned_documents = []
        
        for doc in documents:
            text = doc.page_content
            
            text = re.sub(r'\s+', ' ', text)
            
            text = text.strip()
            
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
            
            text = re.sub(r'\s+', ' ', text)

            text = re.sub(r'Page \d+.*', '', text)
            text = re.sub(r'\b[A-Z\s]{5,}\b', '', text)
            text = re.sub(r'Reference ID:.*', '', text)
            # Update the document with cleaned content
            doc.page_content = text
            cleaned_documents.append(doc)
        
        return cleaned_documents

    def process_file(self, file_name: str, chunk_size: int = 300, overlap: int = 50):
        content = self.get_file_content(file_name)

        if content is None:
            return None

        cleaned_content = self.clean_text(content)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        chunks = splitter.split_documents(cleaned_content)
        return chunks