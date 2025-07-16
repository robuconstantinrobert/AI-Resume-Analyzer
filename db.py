import os
import psycopg2
from dotenv import load_dotenv

from pgvector.psycopg2 import register_vector

load_dotenv(dotenv_path=".env")

def get_conn():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )
    register_vector(conn)
    return conn

def insert_chunks_bulk(chunk_tuples):
    conn = get_conn()
    cur = conn.cursor()
    for tup in chunk_tuples:
        cur.execute(
            "INSERT INTO resume_chunks (filename, chunk_index, chunk_text, embedding) VALUES (%s, %s, %s, %s)",
            tup
        )
    conn.commit()
    cur.close()
    conn.close()

def search_similar_chunks(embedding, top_k=5, offset=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT filename, chunk_index, chunk_text, embedding <-> %s::vector AS distance
        FROM public.resume_chunks
        ORDER BY embedding <-> %s::vector
        LIMIT %s OFFSET %s
        """,
        (embedding, embedding, top_k, offset)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "filename": r[0],
            "chunk_index": r[1],
            "chunk_text": (r[2][:300] + "...") if r[2] else "",
            "distance": r[3]
        }
        for r in rows
    ]
