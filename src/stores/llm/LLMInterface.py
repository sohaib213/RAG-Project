from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    def generate_response(self, prompt: str, chat_history: list = []):
        # Takes a prompt and returns a generated text response
        pass

    @abstractmethod
    def embed(self, text: str, doc_type: str = "passage"):
        # Takes a string and returns a list of floats (the vector)
        pass

    @abstractmethod
    def construct_prompt(self, query: str, role: str = "user"):
        # Builds a message in the format the LLM API expects
        pass