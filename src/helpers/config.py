from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):

    # App info
    APP_NAME: str
    APP_VERSION: str

    # File upload rules
    FILE_ALLOWED_EXTENSIONS: List[str]
    FILE_MAX_SIZE_MB: int
    FILE_CHUNK_SIZE: int

    # MongoDB connection
    MONGODB_URI: str
    MONGODB_DB_NAME: str

    # LLM settings
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str
    GENERATE_RESPONSE_MODEL: str
    GENERATION_BACKEND: str

    # Embedding model
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int

    # Vector database
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METRIC: str

    # Generation controls
    MAX_INPUT_TOKENS: int
    MAX_RESPONSE_TOKENS: int
    TEMPERATURE: float

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()