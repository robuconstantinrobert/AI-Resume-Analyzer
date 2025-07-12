import psycopg2
from pgvector.psycopg2 import register_vector
import os

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    register_vector(conn)
    return conn

def insert_chunk(filename, chunk_index, chunk_text, embedding):
    assert isinstance(embedding, list), "Embedding must be a Python list"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO resume_chunks (filename, chunk_index, chunk_text, embedding)
        VALUES (%s, %s, %s, %s)
        """,
        (filename, chunk_index, chunk_text, embedding)
    )
    conn.commit()
    cur.close()
    conn.close()

def search_similar_chunks(embedding, top_k=5):
    assert isinstance(embedding, list), "Embedding must be a Python list"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT filename, chunk_index, chunk_text, embedding <-> %s::vector AS distance
        FROM public.resume_chunks
        ORDER BY embedding <-> %s::vector
        LIMIT %s
        """,
        (embedding, embedding, top_k)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "filename": r[0],
            "chunk_index": r[1],
            "chunk_text": r[2][:300] + "...",
            "distance": r[3]
        }
        for r in rows
    ]
