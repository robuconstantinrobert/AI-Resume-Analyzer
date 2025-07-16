import io
import pytest
from unittest import mock
from fastapi.testclient import TestClient
import main
import resume_ingest
import db

client = TestClient(main.app)

def test_extract_text_from_pdf_valid(monkeypatch):
    class DummyPage:
        def extract_text(self): return "This is a test PDF."

    class DummyPDF:
        pages = [DummyPage()]
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass

    monkeypatch.setattr("pdfplumber.open", lambda *a, **k: DummyPDF())
    text = resume_ingest.extract_text_from_pdf(b"fakepdf")
    assert "test PDF" in text

def test_extract_text_from_pdf_empty(monkeypatch):
    class DummyPDF:
        pages = []
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
    monkeypatch.setattr("pdfplumber.open", lambda *a, **k: DummyPDF())
    with pytest.raises(ValueError):
        resume_ingest.extract_text_from_pdf(b"fakepdf")

def test_extract_text_from_txt():
    text = resume_ingest.extract_text_from_txt(b"hello world!")
    assert text == "hello world!"

def test_process_resume_file_pdf(monkeypatch):
    monkeypatch.setattr(resume_ingest, "extract_text_from_pdf", lambda x: "hello world. Another chunk here.")
    monkeypatch.setattr(resume_ingest, "embed_chunks", lambda x: [[1.0, 2.0]] * len(x))

    class DummySplitter:
        def split_text(self, text): return ["chunk1", "chunk2"]
    monkeypatch.setattr("langchain.text_splitter.RecursiveCharacterTextSplitter", lambda chunk_size, chunk_overlap: DummySplitter())
    monkeypatch.setattr("db.insert_chunks_bulk", lambda x: None)
    result = resume_ingest.process_resume_file(b"fake", "test.pdf")
    assert isinstance(result, list)
    assert result[0]["text"] == "chunk1"

def test_process_resume_file_txt(monkeypatch):
    monkeypatch.setattr(resume_ingest, "extract_text_from_txt", lambda x: "foo bar baz")
    monkeypatch.setattr(resume_ingest, "embed_chunks", lambda x: [[1.0, 2.0]] * len(x))
    class DummySplitter:
        def split_text(self, text): return ["t1", "t2"]
    monkeypatch.setattr("langchain.text_splitter.RecursiveCharacterTextSplitter", lambda chunk_size, chunk_overlap: DummySplitter())
    monkeypatch.setattr("db.insert_chunks_bulk", lambda x: None)
    result = resume_ingest.process_resume_file(b"somebytes", "file.txt")
    assert len(result) == 2

def test_process_resume_file_unsupported():
    with pytest.raises(ValueError):
        resume_ingest.process_resume_file(b"fake", "file.docx")

def test_process_resume_file_empty(monkeypatch):
    monkeypatch.setattr(resume_ingest, "extract_text_from_txt", lambda x: "")
    with pytest.raises(ValueError):
        resume_ingest.process_resume_file(b"fake", "a.txt")

def test_embed_query(monkeypatch):
    dummy_model = mock.Mock()
    dummy_model.encode.return_value = [[0.1, 0.2, 0.3]]
    monkeypatch.setattr(resume_ingest, "get_embedding_model", lambda: dummy_model)
    result = resume_ingest.embed_query("test query")
    assert result == [0.1, 0.2, 0.3]

def test_call_llm_gemini(monkeypatch):
    dummy_response = mock.Mock()
    dummy_response.text = "AI answer"
    dummy_model = mock.Mock()
    dummy_model.generate_content.return_value = dummy_response
    monkeypatch.setattr("google.generativeai.GenerativeModel", lambda *a, **k: dummy_model)
    monkeypatch.setattr("google.generativeai.configure", lambda api_key: None)
    with mock.patch.dict("os.environ", {"GOOGLE_API_KEY": "abc"}):
        resp = resume_ingest.call_llm_gemini("prompt here")
        assert "AI answer" in resp

def test_call_llm_gemini_no_text(monkeypatch):
    dummy_response = mock.Mock()
    delattr(dummy_response, "text")
    dummy_model = mock.Mock()
    dummy_model.generate_content.return_value = dummy_response
    monkeypatch.setattr("google.generativeai.GenerativeModel", lambda *a, **k: dummy_model)
    monkeypatch.setattr("google.generativeai.configure", lambda api_key: None)
    with mock.patch.dict("os.environ", {"GOOGLE_API_KEY": "abc"}):
        resp = resume_ingest.call_llm_gemini("prompt here")
        assert "object" in str(type(resp)) or isinstance(resp, str)


def test_insert_chunks_bulk(monkeypatch):
    class DummyCur:
        def execute(self, *a, **k): self.called = True
        def close(self): pass
    class DummyConn:
        def cursor(self): return DummyCur()
        def commit(self): pass
        def close(self): pass
    monkeypatch.setattr(db, "get_conn", lambda: DummyConn())
    db.insert_chunks_bulk([("f.txt", 1, "chunk", [0.1, 0.2])])

def test_search_similar_chunks(monkeypatch):
    class DummyCur:
        def execute(self, *a, **k): pass
        def fetchall(self): return [
            ("f.txt", 0, "a"*350, 0.7),
            ("f.txt", 1, None, 0.8)
        ]
        def close(self): pass
    class DummyConn:
        def cursor(self): return DummyCur()
        def close(self): pass
    monkeypatch.setattr(db, "get_conn", lambda: DummyConn())
    results = db.search_similar_chunks([0.1, 0.2], top_k=2)
    assert len(results) == 2
    assert results[0]["chunk_text"].endswith("...")


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    d = resp.json()
    assert "AI Resume Analyzer" in d["message"]

def test_upload_resumes(monkeypatch):
    dummy_result = [{"text": "chunk", "embedding": [0.1, 0.2]}]
    monkeypatch.setattr("resume_ingest.process_resume_file", lambda content, filename: dummy_result)
    test_file = ("resume.txt", io.BytesIO(b"some text"), "text/plain")
    response = client.post("/upload/", files={"files": test_file})
    assert response.status_code == 200
    assert "processed" in response.json()

def test_search_resumes(monkeypatch):
    monkeypatch.setattr("resume_ingest.embed_query", lambda q: [1, 2, 3])
    monkeypatch.setattr("db.search_similar_chunks", lambda emb, top_k, offset: [{"filename": "f", "chunk_text": "t", "distance": 0.1}])
    response = client.post("/search/", json={"query": "ml engineer", "top_k": 1, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data and isinstance(data["results"], list)

def test_rag_chat(monkeypatch):
    monkeypatch.setattr("resume_ingest.embed_query", lambda x: [0.1, 0.2])
    monkeypatch.setattr("db.search_similar_chunks", lambda emb, top_k: [{"chunk_text": "resume chunk"}])
    monkeypatch.setattr("resume_ingest.call_llm_gemini", lambda prompt: "llm output")
    data = {"job_description": "Software developer", "top_k": 1}
    response = client.post("/chat/", json=data)
    assert response.status_code == 200
    result = response.json()
    assert "llm_answer" in result
    assert "matched_chunks" in result

def test_rag_chat_followup(monkeypatch):
    monkeypatch.setattr("resume_ingest.embed_query", lambda x: [0.1, 0.2])
    monkeypatch.setattr("db.search_similar_chunks", lambda emb, top_k: [{"chunk_text": "chunk"}])
    monkeypatch.setattr("resume_ingest.call_llm_gemini", lambda prompt: "llm output 2")
    data = {"job_description": "Analyst", "top_k": 1, "followup": "what about python?"}
    response = client.post("/chat/", json=data)
    assert response.status_code == 200
    assert "llm_answer" in response.json()


if __name__ == "__main__":
    pytest.main([__file__])
