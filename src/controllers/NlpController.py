from controllers.BaseController import BaseController
from stores.llm.tempelate.template_parser import TemplateParser
from rank_bm25 import BM25Okapi
import re

class NlpController(BaseController):

    STOPWORDS = {
        "the", "is", "a", "an", "and", "or", "in", "on", "at", "to", "for"
    }

    def tokenize(self, text):
        text = (text or "").lower()
        tokens = re.findall(r"[a-z0-9]+", text)

        return [t for t in tokens if t not in self.STOPWORDS]

    def contains_arabic(self, text):
        return bool(re.search(r"[\u0600-\u06FF]", text or ""))

    def translate_query_to_english(self, query):
        prompt = (
            "Translate the following Arabic medical question into concise English for document search. "
            "Return only the translated question, without explanations or quotation marks.\n\n"
            f"Arabic question: {query}"
        )
        try:
            translated_query = self.generation_client.generate_response(prompt=prompt)
        except Exception as e:
            print(f"[WARN] Arabic query translation failed: {e}")
            return query

        return translated_query.strip() if translated_query else query


    def normalize_repeated_clause(self, text):
        text = (text or "").lower()
        text = re.sub(r"^[\s\-•\d\.\)]+", "", text)
        text = re.sub(r"^(و|او|أو)\s+", "", text)
        text = re.sub(r"^و(?=ال)", "", text)
        return re.sub(r"\s+", " ", text).strip()


    def remove_repeated_clauses(self, text):
        cleaned_lines = []

        for line in (text or "").splitlines():
            if not line.strip():
                cleaned_lines.append(line)
                continue

            parts = re.split(r"([،,؛;])", line)
            seen = set()
            rebuilt = []

            for index in range(0, len(parts), 2):
                clause = parts[index].strip()
                delimiter = parts[index + 1] if index + 1 < len(parts) else ""

                if not clause:
                    continue

                normalized_clause = self.normalize_repeated_clause(clause)
                if len(normalized_clause) > 2 and normalized_clause in seen:
                    continue

                seen.add(normalized_clause)
                rebuilt.append(clause + delimiter)

            cleaned_lines.append(" ".join(rebuilt).strip())

        return "\n".join(cleaned_lines).strip()


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

        # tokenize the query for BM25; semantic search still works if this is empty
        query_tokens = self.tokenize(query)
        

        # get the collection name for the project
        collection_name = self.get_collection_name(project_id)
        

        # Embed the query BY doc_type="query" not doc_type="passage"
        query_vector = self.embedding_client.embed(query, doc_type="query")


        # search for the most similar chunks in Qdrant using the query vector "SYMANTIC SEARCH"
        vector_results  = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=max(20,top_k*5),
            score_threshold = score_threshold
        )
        if not vector_results:
            return []
        
      
        # search for the most similar chunks in Qdrant "CONTENT SEARCH"
        corpus = [self.tokenize(r.text) for r in vector_results] # divide each document into tokens for BM25
        use_bm25 = bool(query_tokens) and any(corpus)
        bm25_scores = []
        if use_bm25:
            bm25 = BM25Okapi(corpus) # train BM25 on the candidate documents
            bm25_scores = bm25.get_scores(query_tokens) 


       #sort each document by vector similarity and BM25 score
        vec_sorted = sorted(enumerate(vector_results), key=lambda x: x[1].score, reverse=True)
        bm25_sorted = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True) if use_bm25 else []



       # assign ranks based on the sorted order for both vector similarity and BM25 scores
        vec_rank = {idx: rank+1 for rank, (idx, _) in enumerate(vec_sorted)}
        bm25_rank = {idx: rank+1 for rank, (idx, _) in enumerate(bm25_sorted)} if use_bm25 else {}


       # combine the ranks using RRF formula: score =(1 / (k + vec_rank)) +(1 / (k + bm25_rank))
        k = 60
        combined = []
        for i, r in enumerate(vector_results):
            score = (1 / (k + vec_rank[i]))
            if use_bm25:
                score += (1 / (k + bm25_rank[i]))

            combined.append((r, score))


        # sort the combined results by the RRF score in descending order
        combined = sorted(combined, key=lambda x: x[1], reverse=True)


        # remove duplicates
        seen = set()
        final_results = []
        for r, score in combined:  
            key = " ".join(r.text.lower().split())
            if key not in seen:
                seen.add(key)
                final_results.append({"doc": r, "score": score})


        # remove empty
        final_results = [r for r in final_results if r["doc"].text.strip()]
        return final_results[:top_k]


    def prepare_query_for_search(self, query: str, language: str = "en"):
        language = (language or "en").lower()
        if language == "ar" and self.contains_arabic(query):
            return self.translate_query_to_english(query)

        return query


    def search_with_language(self, project_id: str, query: str, top_k: int = 5, language: str = "en"):
        search_query = self.prepare_query_for_search(query=query, language=language)
        return self.search(project_id=project_id, query=search_query, top_k=top_k), search_query


    
    def answer(self, project_id: str, query: str, top_k: int = 5, language: str = "en"):

        # retrieve relevant chunks
        relevant_chunks, search_query = self.search_with_language(
            project_id=project_id,
            query=query,
            top_k=top_k,
            language=language
        )

        if not relevant_chunks:
            if language == "ar":
                return "لم أجد معلومات ذات صلة في الوثائق للإجابة على سؤالك.", None, None

            return "I couldn't find any relevant information to answer your question.", None, None     

        # switch language for prompts
        self.template_parser.set_language(language)
        # load prompt templates
        system_prompt = self.template_parser.get("rag", "system_prompt")
        footer_prompt = self.template_parser.get("rag", "footer_prompt")


        #Build numbered document section from retrieved chunks
        documents_section = ""
        for i, chunk in enumerate(relevant_chunks):
            documents_section += self.template_parser.get(
                "rag", "document_prompt",
                {"doc_num": i + 1, "text": chunk["doc"].text}
            )


        #combine everything into the full prompt
        search_note = ""
        if search_query != query:
            search_note = f"\n## English search query:\n{search_query}\n"

        full_prompt = f"{documents_section}{search_note}\n\n## Question:\n{query}\n\n{footer_prompt}"

        # load chat history with system prompt
        chat_history = [
            self.generation_client.construct_prompt(
                query=system_prompt, role="system"
            )
        ]

        # generate and return the answer
        response  = self.generation_client.generate_response(
            prompt=full_prompt,
            chat_history=chat_history
        )
        response = self.remove_repeated_clauses(response)

        return response , full_prompt, chat_history
