from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., description="User search query")
    top_k: int = Field(default=4, ge=1, le=20)


class SearchResult(BaseModel):
    source: str
    content: str
    score: float
    chunk_id: str
    category: str | None = None
    topic: str | None = None
    audience: str | None = None
    risk_level: str | None = None


class AskRequest(BaseModel):
    question: str = Field(..., description="User question")
    top_k: int = Field(default=4, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    contexts: List[SearchResult]


class IngestResponse(BaseModel):
    documents: int
    chunks: int
    files: List[str]
    collection_name: str


class HealthResponse(BaseModel):
    status: str
    collection_name: str
    chat_model: str
    embedding_model: str
    message: Optional[str] = None
