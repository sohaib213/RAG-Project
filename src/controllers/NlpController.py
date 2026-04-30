from controllers.BaseController import BaseController
from stores.llm.tempelate.template_parser import TemplateParser


class NlpController(BaseController):

    def __init__(self, vectordb_client, generation_client,
                 embedding_client, template_parser: TemplateParser):
        super().__init__()
        # All three clients are injected from main.py
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def get_collection_name(self, project_id: str):
        # Each project gets its own isolated collection in Qdrant
        return f"collection_{project_id}"

    #OG
    def push_to_index(self, project_id: str, chunks: list, do_reset: int = 0):
        collection_name = self.get_collection_name(project_id)

        # Delete the old collection if reset is requested
        if do_reset == 1:
            try:
                self.vectordb_client.delete_collection(collection_name)
            except Exception as e:
                print(f"[WARN] delete_collection failed: {e}")

        # Create the collection using the embedding model's vector size
        if not self.vectordb_client.is_collection_exists(collection_name):
            self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size
            )

        # Embed each chunk and collect the vectors
        valid_chunks = [
            chunk for chunk in chunks
            if chunk.chunk_text and chunk.chunk_text.strip()
        ]
        texts = [
            " ".join(chunk.chunk_text.split())
            for chunk in valid_chunks
        ]
        metadata = [
            chunk.chunk_metadata
            for chunk in valid_chunks
        ]
        vectors = [
            self.embedding_client.embed(text, doc_type="passage")
            for text in texts
        ]

        if not (len(texts) == len(vectors) == len(metadata)):
            raise ValueError(
            f"Embedding alignment mismatch: "
            f"texts={len(texts)}, vectors={len(vectors)}, metadata={len(metadata)}"
            )
        # Store everything in Qdrant
        self.vectordb_client.add_documents(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata
        )
        
        return len(texts)
    def search(self, project_id: str, query: str, top_k: int = 5):
        collection_name = self.get_collection_name(project_id)

        # Embed the query — note doc_type is "query" not "passage"
        query_vector = self.embedding_client.embed(query, doc_type="query")

        # Search for the most similar chunks in Qdrant
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=top_k
        )

        return results

    def answer(self, project_id: str, query: str, top_k: int = 5):
        # Step 1: retrieve relevant chunks
        relevant_chunks = self.search(project_id, query, top_k)

        if not relevant_chunks:
            return None, None, None

        # Step 2: load prompt templates
        system_prompt = self.template_parser.get("rag", "system_prompt")
        footer_prompt = self.template_parser.get("rag", "footer_prompt")

        # Step 3: build the documents section of the prompt
        documents_section = ""
        for i, chunk in enumerate(relevant_chunks):
            documents_section += self.template_parser.get(
                "rag", "document_prompt",
                {"doc_num": i + 1, "text": chunk.text}
            )

        # Step 4: combine everything into the full prompt
        full_prompt = f"{documents_section}\n\n## Question:\n{query}\n\n{footer_prompt}"

        # Step 5: build chat history with system prompt
        chat_history = [
            self.generation_client.construct_prompt(
                query=system_prompt, role="system"
            )
        ]

        # Step 6: generate and return the answer
        answer = self.generation_client.generate_response(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history
