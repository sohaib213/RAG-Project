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

    def clean_text(self, documents):
        cleaned_documents = []
        
        for doc in documents:
            # Get the text content
            text = doc.page_content
            
            # Remove extra whitespace and newlines
            text = re.sub(r'\s+', ' ', text)
            
            # Remove leading/trailing whitespace
            text = text.strip()
            
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
            
            # Remove duplicate spaces again
            text = re.sub(r'\s+', ' ', text)
            # Remove page numbers
            text = re.sub(r'Page \d+.*', '', text)
            # Remove section headers like ALL CAPS
            text = re.sub(r'\b[A-Z\s]{5,}\b', '', text)
            # Remove page headers like "Reference ID"
            text = re.sub(r'Reference ID:.*', '', text)
            # Update the document with cleaned content
            doc.page_content = text
            cleaned_documents.append(doc)
        
        return cleaned_documents

    def process_file(self, file_name: str, chunk_size: int = 800, overlap: int = 100):
        # Step 1: Load the file content
        content = self.get_file_content(file_name)

        if content is None:
            return None

        # Step 2: Clean the data
        cleaned_content = self.clean_text(content)

        # Step 3: Set up the splitter with the given chunk size and overlap
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        # Step 4: Split the cleaned content into chunks and return them
        chunks = splitter.split_documents(cleaned_content)
        return chunks