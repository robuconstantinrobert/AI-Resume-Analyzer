



"""

Resume ingestion and processing
    -> upload parse and chunk resumes PDF and text files
    -> extract and chunk resume text for downstream processing
    -> generate embeddings for each chunk using allMiniLM

Vector Database Integration
    -> store embeddings and metadata in a vector DB -> PostgreSQL and pgvector
    -> perform similarity searches

RAG Chatbot
    -> accept a job description as input
    -> retrieve the most relevant resume chunks
    -> use an LLM to generate conversational answers about candidate fit
    -> support followup questions based on the current job search

Optional
    -> WEB UI
    -> Metadata search
        -> extract and store structured metadata like skills, titles, years of experience, enable SQL search

"""

from fastapi import FastAPI, UploadFile, File, Body
from resume_ingest import process_resume_file, embed_query, call_llm_gemini
from db import search_similar_chunks

app = FastAPI()

@app.post("/upload/")
async def upload_resumes(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        filename = file.filename
        chunked = process_resume_file(content, filename)
        results.append({
            "filename": filename,
            "num_chunks": len(chunked),
            "chunks": [
                {
                    "text": c["text"][:200] + "...",
                    "embedding_preview": c["embedding"][:5]
                }
                for c in chunked[:2]
            ]
        })
    return {"processed": results}


@app.post("/search/")
async def search_resumes(query: str = Body(..., embed=True), top_k: int = 5):
    embedding = embed_query(query)
    results = search_similar_chunks(embedding, top_k=top_k)
    return {"results": results}


@app.post("/chat/")
async def rag_chat(
    job_description: str = Body(..., embed=True),
    top_k: int = 6,
    followup: str = Body(None)
):
    jd_embedding = embed_query(job_description)
    chunks = search_similar_chunks(jd_embedding, top_k=top_k)
    context = "\n\n".join([c["chunk_text"] for c in chunks])

    if not followup:
        prompt = (
            f"You are an AI hiring assistant.\n"
            f"Job Description:\n{job_description}\n\n"
            f"Candidate Resume Excerpts:\n{context}\n\n"
            "Summarize how well the candidate fits this job. Be specific about skills and experience matches."
        )
    else:
        prompt = (
            f"You are an AI hiring assistant.\n"
            f"Job Description:\n{job_description}\n\n"
            f"Candidate Resume Excerpts:\n{context}\n\n"
            f"Previous Q&A and Follow-up:\n{followup}\n\n"
            "Answer the follow-up question using all the above context."
        )

    answer = call_llm_gemini(prompt)
    return {
        "llm_answer": answer,
        "matched_chunks": chunks
    }




