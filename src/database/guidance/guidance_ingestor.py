# src/pipelines/guidance_ingestor.py

from typing import List
from src.models.document import RuleChunk


class GuidanceIngestor:
    def __init__(self, *, guidance_store, embedder):
        self.store = guidance_store
        self.embedder = embedder

    def ingest_hints(self, *, rows: List[dict], truncate:bool = False) -> List[RuleChunk,]:
        rule_chunks: List[RuleChunk] = []

        if truncate:
            self.store.truncate()

        for row in rows:
            embed_content = row.get("embedding")
            if not embed_content:
                continue

            embedding = self.embedder.embed_query(embed_content)

            rule_chunks.append(
                RuleChunk(
                    name=row.get("name"),
                    content=row.get("content"),
                    priority=row.get("priority"),
                    type=row.get("type"),
                    embedding=embedding,
                )
            )

        self.store.insert_rule_chunks(rule_chunks=rule_chunks)
        return "success"
