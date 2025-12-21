from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector

def create_vectorstore():
    embedder = create_embedder()

    vectorstore = PGVector(
        connection_string="postgresql+psycopg2://postgres:57325@localhost:5432/rag_app",
        embedding_function=embedder,
        collection_name="documents",
    )

    return vectorstore

def create_embedder():
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    return embedder

    