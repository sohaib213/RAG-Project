from sentence_transformers import SentenceTransformer
from stores.llm.LLMInterface import LLMInterface


class EmbeddingProvider(LLMInterface):

    def __init__(self, model_id: str, max_length: int):
        # Load the model locally — downloads it on first run
        self.model = SentenceTransformer(model_id)
        self.model.max_seq_length = max_length
        # Store the vector size so the vector DB knows what dimension to use
        self.embedding_size = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str, doc_type: str = "passage"):
        # Add prefix based on whether this is a document or a query
        # This is required by BGE models for better accuracy
        if doc_type == "passage":
            text = f"passage: {text}"
        else:
            text = f"query: {text}"

        vector = self.model.encode(text)
        return vector.tolist()

    def generate_response(self, prompt: str, chat_history: list = []):
        # Embedding models do not generate text
        raise NotImplementedError("This provider only supports embeddings")

    def construct_prompt(self, query: str, role: str = "user"):
        # Not needed for embedding models
        raise NotImplementedError("This provider only supports embeddings")