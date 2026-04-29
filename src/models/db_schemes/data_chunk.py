from pydantic import BaseModel
from typing import Optional


class DataChunk(BaseModel):

    id: str = None
    chunk_text: str
    chunk_metadata: dict
    chunk_order: int
    chunk_project_id: str


class RetrievalDocument(BaseModel):
    # This is what we return after a vector search
    text: str
    score: float