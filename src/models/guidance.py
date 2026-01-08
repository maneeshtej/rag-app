from dataclasses import dataclass
from typing import Optional

@dataclass
class GuidanceIngest:
    name: str
    type: str
    content: str
    priority: int = 0
    active: bool = True

    id: Optional[str] = None
    embedding_text: Optional[str] = None
    embedding: Optional[list[float]] = None
    similarity: Optional[float] = None

    @classmethod
    def from_dict(cls, d: dict, *, embedder=None) -> "GuidanceIngest":
        embedding_text = d.get("embedding_text")

        embedding = (
            embedder.embed(embedding_text)
            if embedder and embedding_text
            else None
        )

        return cls(
            name=d["name"],
            type=d["type"],
            content=d["content"].strip(),
            priority=d.get("priority", 0),
            active=d.get("active", True),
            embedding_text=embedding_text.strip() if embedding_text else None,
            embedding=embedding,
        )

    def to_db_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "priority": self.priority,
            "content": self.content,
            "active": self.active,
        }
    
    def to_prompt_block(self) -> str:
        header = f"[GUIDANCE | {self.type.upper()} | priority={self.priority}]"
        body = self.content.strip()

        return f"{header}\n{body}"

