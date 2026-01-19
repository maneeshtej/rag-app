from langchain_huggingface import HuggingFaceEmbeddings

from src.database.column.column_store import ColumnStore


class ColumnRetriever:
    def __init__(self, *, column_store, embedder):
        """
        column_store: ColumnStore
        embedder: object with embed(text: str) -> list[float]
        """
        self.column_store:ColumnStore = column_store
        self.embedder:HuggingFaceEmbeddings = embedder

    def retrieve(
        self,
        *,
        semantic_column: str,
        table_name: str,
        k: int = 5,
    ) -> list[dict]:
        """
        Returns candidate columns for a semantic column within a table.
        """

        embedding = self.embedder.embed_query(semantic_column)

        

        results = self.column_store.similarity_search(
            embedding=embedding,
            table_name=table_name,
            k=k,
        )

        return results
