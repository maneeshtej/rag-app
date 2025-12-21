# database/documents.py
from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List


@dataclass
class StoredChunk:
    id: UUID
    content: str
    embedding: List[float]
    owner_id: UUID
    role: str
    access_level: int
    source: Optional[str]

@dataclass
class MinimalDocument:
    id: UUID
    content: str
    source: Optional[str]