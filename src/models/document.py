# models/document.py

from dataclasses import dataclass
from datetime import datetime
import json
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
    
    def to_minimal_dict(self) -> dict:
        """
        Minimal rule representation for Pass 1 (NL parsing / normalization).
        """
        return {
            "name": self.name,
            "type": self.type,
            "priority": self.priority,
            "instruction": self.content.strip(),
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
    
    def _load_schema(self) -> dict:
        if isinstance(self.schema, str):
            return json.loads(self.schema)
        return self.schema

    def to_minimal_dict(self) -> dict:
        """
        Minimal, safe schema representation for Pass 1 (NL parsing).
        """
        schema = self._load_schema()

        return {
            "table": self.name,
            "description": schema.get("description", ""),
        }
