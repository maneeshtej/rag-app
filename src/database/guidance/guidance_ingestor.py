# src/pipelines/guidance_ingestor.py

from typing import List
from src.models.document import RuleChunk, SchemaChunk


class GuidanceIngestor:
    def __init__(self, *, guidance_store, embedder):
        self.guidance_store = guidance_store
        self.embedder = embedder

    def ingest_hints(self, *, rows: List[dict], truncate:bool = False) -> str:
        rule_chunks: List[RuleChunk] = []

        if truncate:
            self.guidance_store.truncate_query_rules()

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

        print("inserting rules...")
        result = self.guidance_store.insert_rule_chunks(rule_chunks=rule_chunks)
        return result
    
    def ingest_schema(self, *, rows:list[dict], truncate:bool = False) -> int:

        schema_chunks:list[SchemaChunk] = []

        for row in rows:
            embed_text = row.get("embedding_text")
            if not embed_text:
                continue

            embedding = self.embedder.embed_query(embed_text)

            schema_chunks.append(
                SchemaChunk(
                    name=row.get("name"),
                    schema=row.get("schema"),
                    content=row.get("content", ""),
                    related_tables=row.get("related_tables", []),
                    embedding=embedding,
                )
            )


        if truncate:
            self.guidance_store.truncate_schema_rules()

        return self.guidance_store.insert_schema_chunks(schema_chunks=schema_chunks)


