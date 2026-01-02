import json
from db.vector_db import VectorDB
from db.factory_db import get_vector_db
from embedding_engine import EmbeddingEngine
from document_parser import DocumentParser

from templates import chat_template

from llm.gemini import GeminiLLM
from llm.ollama import OllamaLLM
from llm.dummy import DummyLLM
from llm.base import LLM

def build_llm(model_type: str, **kwargs) -> LLM:
    if model_type == "gemini":
        return GeminiLLM(model_name=kwargs.get("model_name", "gemini-2.5-flash"))
    elif model_type == "ollama":
        return OllamaLLM(model_name=kwargs.get("model_name", "llama3"), base_url=kwargs.get("base_url", "http://localhost:11434"), temperature=kwargs.get("temperature", 0.7))
    else:
        return DummyLLM()

class UploadService:
    def __init__(self, file_path: str, db = None, engine = None):
        self.file_path = file_path
        self.parser = DocumentParser(file_path)
        self.engine = engine or EmbeddingEngine()
        self.db = db or get_vector_db()

    def insert_documents(self):
        if not self.parser:
            print("No document parser initialized. Please provide a valid file path.")
            return

        cleaned_docs = self.parser.clean_documents()

        if not cleaned_docs:
            print("No content to process after cleaning.")
            return

        content = self.parser.split_documents()
        texts = [doc.page_content for doc in content]
        embeddings = self.engine.generate_embeddings(texts)

        print(f"Generated embeddings for {len(embeddings)} documents.")

        data_to_insert = []
        for i, doc in enumerate(content):
            data_to_insert.append((doc.page_content, json.dumps({}), embeddings[i]))

        print(f"Inserting {len(data_to_insert)} documents into the vector database.")

        self.db.insert_documents(data_to_insert)


class LLMService:
    def __init__(self, llm: LLM, embedding_engine: EmbeddingEngine | None = None, db = None):
        self.llm = llm
        self.db = db or get_vector_db()
        self.engine = embedding_engine or EmbeddingEngine()
        
    def _query(self, query, top_k=5):
        query_embedding = self.engine.generate_embeddings([query])[0]
        results = self.db.search(query_embedding, limit=top_k)
        return results

    def answer(self, question: str):
        if self.db.is_empty():
            return "The vector database is empty. Please upload documents first."

        similar_docs = self._query(question, top_k=6)
        context = "\n".join([doc[1] for doc in similar_docs])

        prompt = chat_template.format(context=context, question=question)
        response = self.llm.generate_text(prompt)

        return response


class DBService:
    def __init__(self, db = None):
        self.db = db or get_vector_db()

    def check_empty(self) -> bool:
        return self.db.is_empty()
        
    def clear_database(self):
        self.db.delete_all_documents()
