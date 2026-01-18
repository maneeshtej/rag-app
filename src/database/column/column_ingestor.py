from langchain_huggingface import HuggingFaceEmbeddings
import psycopg2

from src.database.column.column_store import ColumnStore
from src.database.db import get_dev_connection
from src.database.dependencies import create_embedder
from src.schema.columns.column import column_list


class ColumnsIngestor:
    def __init__(self, *, column_store, embedder):
        self.column_store:ColumnStore = column_store
        self.embedder:HuggingFaceEmbeddings = embedder

    def ingest(self, columns: list[dict]):
        for col in columns:
            for text in col["texts"]:
                embedding = self.embedder.embed_query(text)

                self.column_store.insert_column(
                    table_name=col["table_name"],
                    column_name=col["column_name"],
                    embedding=embedding,
                )

def main():
    # DB connection
    conn = get_dev_connection()

    column_store = ColumnStore(conn)
    embedder = create_embedder()  # must expose embed(text) -> list[float]

    ingestor = ColumnsIngestor(
        column_store=column_store,
        embedder=embedder,
    )

    # combine all column definitions
    try:
        ingestor.ingest(columns=column_list)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

    print("Column ingestion completed successfully")
if __name__ == "__main__":
    main()
