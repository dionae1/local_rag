import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

class VectorDB:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "semantic_search_db"),
                user=os.getenv("DB_USER", "vector_admin"),
                password=os.getenv("DB_PASSWORD", "vector_password"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5433")
            )
            self.conn.autocommit = False
            self.create_table()


        except Exception as e:
            raise Exception(f"Database connection failed: {e}")
        
    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS embeddings.documents (
            id BIGSERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}',
            embedding vector(384),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS document_embedding_idx
        ON embeddings.documents
        USING hnsw (embedding vector_cosine_ops);
        """

        with self.conn.cursor() as cursor:
            cursor.execute(create_table_query)
            self.conn.commit()

    def insert_documents(self, data: list[tuple]):
        insert_query = """
        INSERT INTO embeddings.documents (content, metadata, embedding)
        VALUES %s
        """

        with self.conn.cursor() as cursor:
            execute_values(cursor, insert_query, data)
            self.conn.commit()
            print(f"Inserted {len(data)} documents.")

    
    def search(self, query_vector: list[float], limit: int = 5) -> list[tuple]:
        """
        - Row[0]: id
        - Row[1]: content
        - Row[2]: metadata
        - Row[3]: similarity
        """
        search_query = """
        SELECT id, content, metadata, 1 - (embedding <=> %s::vector) AS similarity
        FROM embeddings.documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """

        with self.conn.cursor() as cursor:
            cursor.execute(search_query, (query_vector, query_vector, limit))
            rows = cursor.fetchall()
            return rows
        

    def delete_all_documents(self):
        delete_query = "TRUNCATE TABLE embeddings.documents RESTART IDENTITY;"

        with self.conn.cursor() as cursor:
            cursor.execute(delete_query)
            self.conn.commit()
            print("All documents deleted.")


    def is_empty(self) -> bool:
        count_query = "SELECT COUNT(*) FROM embeddings.documents;"

        with self.conn.cursor() as cursor:
            cursor.execute(count_query)
            result = cursor.fetchone()
            if not result:
                return True
            return result[0] == 0

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    vector_db = VectorDB()
    print("VectorDB initialized successfully.")
    vector_db.close()