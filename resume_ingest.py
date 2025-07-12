import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from sentence_transformers import SentenceTransformer
from db import insert_chunk
import os
import google.generativeai as genai


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def embed_chunks(chunks: list[str]):
    return embedding_model.encode(chunks).tolist()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import pdfplumber
    import warnings
    text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            except Exception as e:
                warnings.warn(f"Could not extract text from a page: {e}")
    if not text:
        raise ValueError("No extractable text found in PDF.")
    return "\n".join(text)


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode('utf-8', errors='ignore')


def process_resume_file(file_bytes: bytes, filename: str):
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".txt"):
        text = extract_text_from_txt(file_bytes)
    else:
        raise ValueError("Unsupported file type")
    if not text or not text.strip():
        raise ValueError("No text found in resume.")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80,
    )
    chunks = splitter.split_text(text)
    if not chunks:
        raise ValueError("Chunking produced no output.")

    embeddings = embed_chunks(chunks)
    result = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        print(type(embedding), len(embedding))
        insert_chunk(filename, i, chunk, embedding)
        result.append({
            "text": chunk,
            "embedding": embedding
        })
    return result



def embed_query(query: str):
    return embedding_model.encode([query])[0].tolist()


def call_llm_gemini(prompt: str) -> str:
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    if hasattr(response, "text"):
        return response.text.strip()
    else:
        return str(response)

