import json
from vector_db import VectorDB
from embedding_engine import EmbeddingEngine
from document_parser import DocumentParser

from langchain_ollama import OllamaLLM
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

gemini_chat = GoogleGenerativeAI(model="gemini-2.5-flash")
ollama_chat = OllamaLLM(model="llama3", base_url="http://localhost:11434", temperature=0.7)

chat_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
                You are a helpful assistant that helps answer questions based on provided documents. Use the information from the documents to formulate your answers.
                If the documents do not contain relevant information, respond politely that you do not have the necessary information.
                Documents:
                    {context}

                Question:
                    {question}

            """,
)


class UploadService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parser = DocumentParser(file_path)
        self.db = VectorDB()
        self.engine = EmbeddingEngine()

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


class DBEngineService:
    def __init__(self):
        self.db = VectorDB()
        self.engine = EmbeddingEngine()
        
    def _query(self, query, top_k=5):
        query_embedding = self.engine.generate_embeddings([query])[0]
        results = self.db.search(query_embedding, limit=top_k)
        return results

    def _answer(self, question: str, model: str):
        if self.db.is_empty():
            return "The vector database is empty. Please upload documents first."

        similar_docs = self._query(question, top_k=6)
        context = "\n".join([doc[1] for doc in similar_docs])

        prompt = chat_template.format(context=context, question=question)

        response = ""

        if model == "gemini":
            response = gemini_chat.invoke(prompt)

        elif model == "ollama":
            response = ollama_chat.invoke(prompt)

        return response

    def gemini_answer(self, question: str):
        return self._answer(question, model="gemini")
    
    def ollama_answer(self, question: str):
        return self._answer(question, model="ollama")


class DBService:
    def __init__(self):
        self.db = VectorDB()

    def check_empty(self) -> bool:
        return self.db.is_empty()
        
    def clear_database(self):
        self.db.delete_all_documents()