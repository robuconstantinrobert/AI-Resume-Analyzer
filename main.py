
from fastapi import FastAPI, UploadFile, File, Body
from resume_ingest import process_resume_task, embed_query, call_llm_gemini
from db import search_similar_chunks
from celery_app import celery

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "AI Resume Analyzer API is running.",
        "endpoints": [
            "/upload/",
            "/upload_status/{task_id}",
            "/search/",
            "/chat/"
        ]
    }


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload/")
async def upload_resumes(files: list[UploadFile] = File(...)):
    tasks = []
    for file in files:
        content = await file.read()
        filename = file.filename
        task = process_resume_task.delay(content, filename)
        tasks.append({"filename": filename, "task_id": task.id})
    return {"submitted": tasks}


@app.post("/search/")
async def search_resumes(query: str = Body(..., embed=True), top_k: int = 5, offset: int = 0):
    embedding = embed_query(query)
    results = search_similar_chunks(embedding, top_k=top_k, offset=offset)
    return {"results": results}


@app.get("/upload_status/{task_id}")
async def get_upload_status(task_id: str):
    async_result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": async_result.status,
        "result": async_result.result if async_result.ready() else None
    }


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




