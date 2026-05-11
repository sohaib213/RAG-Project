from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_EXTENSIONS: List[str]
    FILE_MAX_SIZE_MB: int
    FILE_CHUNK_SIZE: int

    MONGODB_URI: str
    MONGODB_DB_NAME: str

    OPENAI_API_KEY: str
    OPENAI_API_BASE: str
    GENERATE_RESPONSE_MODEL: str
    GENERATION_BACKEND: str

    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int

    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METRIC: str

    MAX_INPUT_TOKENS: int
    MAX_RESPONSE_TOKENS: int
    TEMPERATURE: float

    QDRANT_URL: str
    QDRANT_API_KEY: str
    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()