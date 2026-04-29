from pydantic import BaseModel


class PushRequest(BaseModel):
    do_reset: int = 0


class SearchRequest(BaseModel):
    text: str
    top_k: int = 5