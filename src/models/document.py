# models/document.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from sympy import content

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
    embedding: Optional[list[float]] = None
    similarity: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "type": self.type,
            "priority": self.priority,
            "similarity": self.similarity,
        }

@dataclass
class SchemaChunk:
    name: str
    schema: str

    content: Optional[str] = None
    related_tables: Optional[list[str]] = None
    embedding: Optional[list[float]] = None
    similarity: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "schema": self.schema,
            "content": self.content,
            "related_tables": self.related_tables,
            "similarity": self.similarity,
        }
