from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    def generate_response(self, prompt: str, chat_history: list = []):
        pass

    @abstractmethod
    def embed(self, text: str, doc_type: str = "passage"):
        pass

    @abstractmethod
    def construct_prompt(self, query: str, role: str = "user"):
        pass