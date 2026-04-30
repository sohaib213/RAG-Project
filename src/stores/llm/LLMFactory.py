from helpers import get_settings
from stores.llm.provider.OpenAIProvider import OpenAIProvider
from stores.llm.provider.EmbeddingProvider import EmbeddingProvider


class LLMFactory:

    def __init__(self):
        self.settings = get_settings()

    def create_generation_client(self):
        # Read which backend to use from the .env file
        backend = self.settings.GENERATION_BACKEND.lower()

        if backend == "openai":
            return OpenAIProvider(
                api_key=self.settings.OPENAI_API_KEY,
                api_base=self.settings.OPENAI_API_BASE,
                model=self.settings.GENERATE_RESPONSE_MODEL,
                max_tokens=self.settings.MAX_RESPONSE_TOKENS,
                temperature=self.settings.TEMPERATURE
            )

        raise ValueError(f"Unknown generation backend: {backend}")

    def create_embedding_client(self):
        # Always use the local embedding model
        return EmbeddingProvider(
            model_id=self.settings.EMBEDDING_MODEL_ID,
            max_length=self.settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH
        )