from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, Iterable, List

import chromadb
from openai import OpenAI
from pypdf import PdfReader

from backend.config import AppConfig


class RagService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.config.vector_store_dir.mkdir(parents=True, exist_ok=True)
        self.config.documents_dir.mkdir(parents=True, exist_ok=True)
        self.config.processed_dir.mkdir(parents=True, exist_ok=True)
        self.config.raw_sources_dir.mkdir(parents=True, exist_ok=True)
        self.client = OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
        )
        self.vector_client = chromadb.PersistentClient(path=str(config.vector_store_dir))
        self.collection = self.vector_client.get_or_create_collection(
            name=config.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def collection_count(self) -> int:
        return self.collection.count()

    def bootstrap_processed_knowledge(self) -> Dict[str, object]:
        files = sorted(self.config.processed_dir.glob("*.jsonl"))
        if not files:
            return {
                "documents": 0,
                "chunks": 0,
                "files": [],
                "collection_name": self.config.collection_name,
            }
        if self.collection_count() > 0:
            return {
                "documents": 0,
                "chunks": self.collection_count(),
                "files": [path.name for path in files],
                "collection_name": self.config.collection_name,
            }
        return self.ingest_files(files)

    def ingest_files(self, file_paths: Iterable[Path]) -> Dict[str, object]:
        total_chunks = 0
        files = []

        for file_path in file_paths:
            if file_path.suffix.lower() == ".jsonl":
                count = self._ingest_jsonl(file_path)
                if count:
                    total_chunks += count
                    files.append(file_path.name)
                continue

            content = self._extract_text(file_path)
            chunks = self._split_text(content)
            if not chunks:
                continue

            embeddings = self._embed_texts(chunks)
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [
                {
                    "source": file_path.name,
                    "chunk_index": idx,
                    "path": str(file_path),
                }
                for idx, _ in enumerate(chunks)
            ]
            self.collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            total_chunks += len(chunks)
            files.append(file_path.name)

        return {
            "documents": len(files),
            "chunks": total_chunks,
            "files": files,
            "collection_name": self.config.collection_name,
        }

    def reset_collection(self) -> None:
        self.vector_client.delete_collection(name=self.config.collection_name)
        self.collection = self.vector_client.get_or_create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def search(self, query: str, top_k: int | None = None) -> List[Dict[str, object]]:
        query_embedding = self._embed_texts([query])[0]
        response = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k or self.config.top_k,
            include=["documents", "metadatas", "distances"],
        )
        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]

        results: List[Dict[str, object]] = []
        for idx, content in enumerate(documents):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            distance = distances[idx] if idx < len(distances) else 0.0
            score = 1.0 - float(distance)
            results.append(
                {
                    "source": metadata.get("source", "unknown"),
                    "content": content,
                    "score": score,
                    "chunk_id": f"{metadata.get('source', 'unknown')}#{metadata.get('chunk_index', idx)}",
                    "category": metadata.get("category", ""),
                    "topic": metadata.get("topic", ""),
                    "audience": metadata.get("audience", ""),
                    "risk_level": metadata.get("risk_level", ""),
                }
            )
        return results

    def answer_question(self, question: str, top_k: int | None = None) -> Dict[str, object]:
        contexts = self.search(question, top_k=top_k)
        if not contexts:
            return {
                "answer": "知识库中暂无可用内容，请先上传并索引文档。",
                "contexts": [],
            }

        context_block = "\n\n".join(
            [
                f"[{idx}] Source: {item['source']}\nContent:\n{item['content']}"
                for idx, item in enumerate(contexts, start=1)
            ]
        )

        completion = self.client.chat.completions.create(
            model=self.config.chat_model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一名教育心理学与学校心理支持知识库助手。"
                        "只依据提供的检索上下文回答，不要编造事实，不做临床诊断。"
                        "回答时优先服务学生、家长和一线教师，语气专业、温和、支持性。"
                        "遇到自伤、自杀、暴力风险、严重抑郁、持续失眠或明显功能受损等高风险内容时，"
                        "必须明确建议立刻联系监护人、学校心理老师、当地紧急援助或专业心理卫生机构。"
                        "若证据不足，请直接说明资料不足。引用请使用 [1]、[2] 格式。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        f"Context:\n{context_block}\n\n"
                        "请按以下结构作答：\n"
                        "1. 直接回答\n"
                        "2. 原因或机制\n"
                        "3. 可执行建议\n"
                        "4. 风险提醒或何时求助\n"
                        "答案要简洁准确，并带明确引用。"
                    ),
                },
            ],
        )
        answer = completion.choices[0].message.content or ""
        return {"answer": answer, "contexts": contexts}

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.config.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def _extract_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in {".md", ".txt"}:
            return file_path.read_text(encoding="utf-8")
        if suffix == ".pdf":
            reader = PdfReader(str(file_path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _ingest_jsonl(self, file_path: Path) -> int:
        lines = [line for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            return 0

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, object]] = []

        for line in lines:
            item = json.loads(line)
            content = str(item.get("content", "")).strip()
            if not content:
                continue

            source_name = str(item.get("source_title") or item.get("source") or file_path.name)
            record_id = str(item.get("id") or uuid.uuid4())
            ids.append(record_id)
            documents.append(content)
            metadatas.append(
                {
                    "source": source_name,
                    "chunk_index": item.get("chunk_index", 0),
                    "path": str(file_path),
                    "category": item.get("category", ""),
                    "topic": item.get("topic", ""),
                    "audience": item.get("audience", ""),
                    "risk_level": item.get("risk_level", ""),
                    "source_year": item.get("source_year", ""),
                    "source_url": item.get("source_url", ""),
                }
            )

        if not documents:
            return 0

        embeddings = self._embed_texts(documents)
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(documents)

    def _split_text(self, text: str) -> List[str]:
        normalized = " ".join(text.split())
        if not normalized:
            return []

        size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        chunks: List[str] = []
        start = 0
        while start < len(normalized):
            end = min(start + size, len(normalized))
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(normalized):
                break
            start = max(end - overlap, start + 1)
        return chunks
