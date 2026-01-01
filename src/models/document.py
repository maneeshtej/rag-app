# models/document.py

from dataclasses import dataclass
from datetime import datetime
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
    metadata: dict

@dataclass 
class RuleChunk:
    name: str
    content: str
    type: str
    priority: int

    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    embedding: Optional[list[float]] = None
