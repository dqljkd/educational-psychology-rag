from __future__ import annotations

from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile

from backend.config import AppConfig
from backend.models import AskRequest, AskResponse, HealthResponse, IngestResponse, SearchRequest, SearchResult
from backend.rag_service import RagService


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

config = AppConfig.from_env(BASE_DIR)
service = RagService(config)
app = FastAPI(title="RAG Knowledge Base API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    status = "ok" if config.openai_api_key else "warning"
    message = None if config.openai_api_key else "OPENAI_API_KEY is not configured."
    return HealthResponse(
        status=status,
        collection_name=config.collection_name,
        chat_model=config.chat_model,
        embedding_model=config.embedding_model,
        message=message,
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest(files: List[UploadFile] = File(...)) -> IngestResponse:
    saved_paths: List[Path] = []
    for upload in files:
        destination = config.documents_dir / upload.filename
        destination.write_bytes(await upload.read())
        saved_paths.append(destination)
    result = service.ingest_files(saved_paths)
    return IngestResponse(**result)


@app.post("/search", response_model=List[SearchResult])
def search(payload: SearchRequest) -> List[SearchResult]:
    return [SearchResult(**item) for item in service.search(payload.query, payload.top_k)]


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    result = service.answer_question(payload.question, payload.top_k)
    contexts = [SearchResult(**item) for item in result["contexts"]]
    return AskResponse(answer=result["answer"], contexts=contexts)
