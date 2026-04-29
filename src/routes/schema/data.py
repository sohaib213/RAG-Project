from pydantic import BaseModel


class ProcessRequest(BaseModel):
    file_name: str
    chunk_size: int = 500
    overlap: int = 50
    do_reset: int = 0