from typing import List
from uuid import UUID, uuid4
from langchain_core.documents import Document

from src.models.document import RuleChunk, StoredChunk, StoredFile
from src.models.user import User


class GuidanceStore:
    def __init__(self, *, conn, embedder):

        self.conn = conn
        self.embedder = embedder

    def ingest_schema(self, docs: List[Document]):
        # file_id = uuid4()
        # meta = docs[0].metadata

        # stored_file = StoredFile(
        #     id=file_id,
        #     owner_id=UUID(meta["owner_id"]),
        #     role=meta["role"],
        #     access_level=meta["access_level"],
        #     source="schema:all",
        # )

        # texts = [doc.page_content for doc in docs]
        # embeddings = self.vector_store.embedder.embed_documents(texts)

        # stored_chunks = [
        #     StoredChunk(
        #         id=uuid4(),
        #         file_id=file_id,
        #         content=doc.page_content,
        #         embedding=emb,
        #         metadata=doc.metadata or {},
                
        #     )
        #     for doc, emb in zip(docs, embeddings)
        # ]

        # try:
        #     self.vector_store.insert_file(file=stored_file)
        #     self.vector_store.insert_chunks(chunks=stored_chunks, type="table")
        #     self.vector_store.conn.commit()
        # except Exception as e:
        #     self.vector_store.conn.rollback()
        #     raise Exception(e)

        return "schema_ingested"
    
    def ingest_hints(self, rows: list[dict]) -> None:
        rule_chunks: list[RuleChunk] = []

        try:
            # build chunks + embeddings
            for row in rows:
                embed_content = row.get("embedding")
                if not embed_content:
                    continue

                embedding = self.embedder.embed_query(embed_content)

                rule_chunks.append(
                    RuleChunk(
                        name=row.get("name"),
                        content=row.get("content"),
                        type=row.get("type"),
                        priority=row.get("priority"),
                        embedding=embedding
                    )
                )

            query = """
                INSERT INTO query_rules (name, content, priority, type, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """

            # insert into DB
            with self.conn.cursor() as cur:
                for chunk in rule_chunks:
                    cur.execute(
                        query,
                        (
                            chunk.name,
                            chunk.content,
                            chunk.priority,
                            chunk.type,
                            chunk.embedding
                        )
                    )

            self.conn.commit()
            return "success"
        except Exception:
            self.conn.rollback()
            raise

    def semantic_search(
        self,
        *,
        query_embedding: list[float],
        user: User,
        type: str,
        k: int = 5,
    ) -> list[RuleChunk]:

        sql = """
            SELECT name, content, priority, type
            FROM query_rules
            WHERE embedding IS NOT NULL
            AND type = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        type,
                        query_embedding,
                        k
                    )
                )
                rows = cur.fetchall()

            rule_chunks: list[RuleChunk] = [
                RuleChunk(
                        name=row[0],
                        content=row[1],
                        priority=row[2],
                        type=row[3]
                ) for row in rows
            ]

            return rule_chunks

        except Exception:
            self.conn.rollback()
            raise


    def retrieve(self, *, query:str, user:User, k:int = 5, type:str = "table") -> List:
        return self.vector_retriever.retrieve(
                 query=query,
                 user=user,
                 k=k,
                 type=type
            )