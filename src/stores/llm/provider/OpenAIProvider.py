from openai import OpenAI
from src.stores.llm.LLMInterface import LLMInterface


class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_base: str, model: str,
                 max_tokens: int, temperature: float):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_response(self, prompt: str, chat_history: list = []):
        # Add the user prompt to the chat history
        messages = chat_history.copy()
        messages.append(self.construct_prompt(query=prompt, role="user"))

        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        # Return just the text of the response
        return response.choices[0].message.content

    def embed(self, text: str, doc_type: str = "passage"):
        # Call the OpenAI embeddings API and return the vector
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def construct_prompt(self, query: str, role: str = "user"):
        # Build a message dict in the format OpenAI expects
        return {"role": role, "content": query}