from datetime import datetime
from uuid import UUID
from dataclasses import dataclass
from typing import List
from langchain_core.documents import Document


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: UUID
    file_id: UUID
    content: str
    similarity: float
    owner_id: UUID
    role: str
    access_level: int
    source: str | None
    metadata: dict
    created_at: datetime

    @staticmethod
    def to_langchain_docs(chunks: List["RetrievedChunk"]) -> List[Document]:
        return [
            Document(
                page_content=chunk.content,
                metadata={
                    **(chunk.metadata or {}),
                    "chunk_id": str(chunk.chunk_id),
                    "file_id": str(chunk.file_id),
                    "owner_id": str(chunk.owner_id),
                    "role": chunk.role,
                    "access_level": chunk.access_level,
                    "source": chunk.source,
                    "similarity": chunk.similarity,
                },
            )
            for chunk in chunks
        ]

    @staticmethod
    def from_langchain_doc(doc: Document) -> "RetrievedChunk":
        m = doc.metadata or {}

        return RetrievedChunk(
            chunk_id=UUID(m["chunk_id"]),
            file_id=UUID(m["file_id"]),
            content=doc.page_content,
            similarity=float(m.get("similarity", 0.0)),
            owner_id=UUID(m["owner_id"]),
            role=m["role"],
            access_level=int(m["access_level"]),
            source=m.get("source"),
            metadata={
                k: v
                for k, v in m.items()
                if k
                not in {
                    "chunk_id",
                    "file_id",
                    "owner_id",
                    "role",
                    "access_level",
                    "source",
                    "similarity",
                }
            },
        )

    @staticmethod
    def from_langchain_docs(docs: List[Document]) -> List["RetrievedChunk"]:
        return [RetrievedChunk.from_langchain_doc(d) for d in docs]
