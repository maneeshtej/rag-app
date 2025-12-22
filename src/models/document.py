# models/document.py

from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List

@dataclass
class StoredFile:
    id: UUID
    owner_id: UUID
    role: str
    access_level: int
    source: Optional[str]

@dataclass
class StoredChunk:
    id: UUID
    file_id: UUID
    content: str
    embedding: List[float]
