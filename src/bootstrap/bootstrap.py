from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.database.db import get_connection
from src.database.vector.vector_store import VectorStore
from src.database.vector.vector_retriever import VectorRetriever
from src.database.llm import create_vision_llm, create_google_llm
from src.database.dependencies import create_embedder
from src.database.guidance.guidance_store import GuidanceStore

from src.pipelines.vector_ingestion import VectorIngestion
from src.pipelines.vector_retrieval import VectorRetrieval
from src.pipelines.answer_pipeline import AnswerPipeline
from src.pipelines.sql_ingestion import SQLIngestion
from src.pipeline import MainPipeline


# ---------- Shared resources ----------

def create_connection():
    print('loaded connection')
    return get_connection()


def create_text_splitter():
    print('loaded splitter')
    return RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=500,
        chunk_overlap=50,
    )


def create_vector_store(conn):
    print('loaded vector store')
    embedder = create_embedder()
    return VectorStore(
        embedder=embedder,
        conn=conn,
    )

def create_guidance_store(vector_store, vector_retriever):
    print('loaded vector store')
    return GuidanceStore(vector_store=vector_store, vector_retriever=vector_retriever)


def create_vector_retriever(vector_store):
    print('loaded vector retriever')
    return VectorRetriever(
        vector_store=vector_store
    )


def create_llms():
    return {
        "llm": create_google_llm(),
        "vision_llm": create_vision_llm(),
    }


# ---------- Pipeline factories ----------

def create_vector_ingestion(vector_store):
    return VectorIngestion(
        splitter=create_text_splitter(),
        vectorstore=vector_store,
    )


def create_vector_retrieval(vector_retriever):
    return VectorRetrieval(
        retriever=vector_retriever,
    )


def create_sql_ingestion(conn, llms):
    return SQLIngestion(
        conn=conn,
        llm=llms["llm"],
        vision_llm=llms["vision_llm"],
    )


def create_answer_pipeline(llm):
    return AnswerPipeline(
        llm=llm,
    )


# ---------- App wiring ----------

def create_app() -> MainPipeline:
    conn = create_connection()
    llms = create_llms()

    vector_store = create_vector_store(conn)
    vector_retriever = create_vector_retriever(vector_store)

    return MainPipeline(
        vector_ingestion=create_vector_ingestion(vector_store=vector_store),
        vector_retriever=create_vector_retrieval(vector_retriever=vector_retriever),
        sql_ingestion=create_sql_ingestion(conn=conn, llms=llms),
        answer=create_answer_pipeline(llm=llms["llm"]),
        vector_store=vector_store,
        guidance_store=create_guidance_store(vector_store=vector_store, vector_retriever=vector_retriever)
    )
