# main_pipeline_setup.py
from pathlib import Path
from uuid import uuid4
import psycopg2
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.database.dependencies import create_embedder
from src.database.llm import create_google_llm
from src.database.vector.vector_ingestor import VectorIngestor
from src.database.vector.vector_reranker import DeterministicReranker
from src.database.vector.vector_retriever import VectorRetriever
from src.database.vector.vector_store import VectorStore
from src.pipeline import MainPipeline
from src.pipelines.inference.answer_generator import AnswerGenerator
from src.pipelines.vector.vector_ingestion import VectorIngestion
from src.pipelines.vector.vetor_retrieval import VectorRetrieval

def get_loader(path: str):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(path)
    if ext in {".txt", ".md"}:
        return TextLoader(path, encoding="utf-8")
    raise ValueError("Unsupported file type")

def build_app():
    conn = psycopg2.connect(
        dbname="rag_test",
        user="postgres",
        password="12345",
        host="localhost",
        port=5432,
    )

    llm = create_google_llm()
    embedder = create_embedder()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    vector_store = VectorStore(conn=conn)
    retriever = VectorRetriever(vector_store=vector_store)
    vector_ingestor = VectorIngestor(embedder, vector_store)
    vector_ingestion = VectorIngestion(splitter, vector_ingestor)
    vector_retrieval = VectorRetrieval(
        retriever=retriever,
        reranker=DeterministicReranker(),
        embedder=embedder,
    )

    app = MainPipeline(
        vector_ingestion=vector_ingestion,
        vector_retrieval=vector_retrieval,
        answer=AnswerGenerator(llm),
    )

    return app, conn, get_loader
