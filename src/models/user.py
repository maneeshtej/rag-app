from dataclasses import dataclass
from uuid import UUID

@dataclass
class User:
    id: UUID
    username: str
    role: str
    access_level: int