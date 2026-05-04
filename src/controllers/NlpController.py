from controllers.BaseController import BaseController
from stores.llm.tempelate.template_parser import TemplateParser
from rank_bm25 import BM25Okapi
import re

class NlpController(BaseController):
    
    def tokenize(self,text):
        return re.findall(r'\b\w+\b', text.lower())

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
    

    
    # updated to prevent halthenation
    # we dont want just close meaning for spacefic anticpations
    def search(self, project_id: str, query: str, top_k: int = 5, score_threshold: float = 0.2):
        collection_name = self.get_collection_name(project_id)

        # Embed the query — note doc_type is "query" not "passage"
        query_vector = self.embedding_client.embed(query, doc_type="query")

        # search for the most similar chunks in Qdrant
        vector_results  = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=top_k*3,
            score_threshold = score_threshold
        )
        if not vector_results:
            return []
        
        # keyword search
        # keyword_results = self.search_keyword(query, vector_results) 

        # apply bm25 on candidates to capture exact keyword relevance
        query_tokens = self.tokenize(query)
        corpus = [self.tokenize(r.text) for r in vector_results]
        bm25 = BM25Okapi(corpus)
        bm25_scores = bm25.get_scores(query_tokens)

        # normalize scores so vector and BM25 scores to the same scale
        # normalize bm25
        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 else 1
        normalized_bm25 = [s / max_bm25 if max_bm25 != 0 else 0 for s in bm25_scores]

        # normalize vector
        vec_scores = [r.score for r in vector_results]
        max_vec = max(vec_scores) if len(vec_scores) > 0 else 1
        normalized_vec = [s / max_vec if max_vec != 0 else 0 for s in vec_scores]

        # combine semantic and keyword scores into a hybrid score
        combined = []
        for i, r in enumerate(vector_results):
            # if r.text in keyword_results:
            #     score += 0.3 

            # vector_score: context 
            # bm25_scores: keywords
            hybrid_score = (normalized_vec[i] * 0.7) + (normalized_bm25[i] * 0.3)

            # boost score if query terms explicitly appear in the document
            if any(token in r.text.lower() for token in query_tokens):
                hybrid_score += 0.1
            combined.append((r, hybrid_score))

        # sort by score
        combined = sorted(combined, key=lambda x: x[1], reverse=True)
        # remove duplicates
        seen = set()
        final_results = []
        for r, score in combined:  
            key = r.text.strip().lower()
            if key not in seen:
                seen.add(key)
                final_results.append(r)

        # remove empty
        final_results = [r for r in final_results if r.text.strip()]
        return final_results[:top_k]
    

   # option: score_threshold can be added to filter low-relevance result :)
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
