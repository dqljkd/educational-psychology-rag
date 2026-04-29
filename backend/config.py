from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    base_dir: Path
    openai_api_key: str
    openai_base_url: str
    chat_model: str
    embedding_model: str
    collection_name: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    vector_store_dir: Path
    documents_dir: Path
    processed_dir: Path
    raw_sources_dir: Path

    @classmethod
    def from_env(cls, base_dir: Path) -> "AppConfig":
        return cls(
            base_dir=base_dir,
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            collection_name=os.getenv("RAG_COLLECTION_NAME", "knowledge_base"),
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "800")),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "120")),
            top_k=int(os.getenv("RAG_TOP_K", "4")),
            vector_store_dir=base_dir / "data" / "vector_store",
            documents_dir=base_dir / "data" / "documents",
            processed_dir=base_dir / "data" / "processed",
            raw_sources_dir=base_dir / "data" / "raw_sources",
        )
