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

def insert_chunks_bulk(chunk_tuples):
    """
    chunk_tuples: list of tuples (filename, chunk_index, chunk_text, embedding)
    """
    conn = get_conn()
    cur = conn.cursor()
    args_str = ",".join(cur.mogrify("(%s, %s, %s, %s)", x).decode("utf-8") for x in chunk_tuples)
    cur.execute(
        f"INSERT INTO resume_chunks (filename, chunk_index, chunk_text, embedding) VALUES {args_str}"
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
            "chunk_text": r[2][:300] + "...",
            "distance": r[3]
        }
        for r in rows
    ]