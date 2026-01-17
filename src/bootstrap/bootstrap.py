from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.database.entity.entity_ingestor import EntityIngestor
from src.database.entity.entity_retriever import EntityRetriever
from src.database.entity.entity_store import EntityStore
from src.database.guidance import guidance_store
from src.database.guidance.guidance_ingestor import GuidanceIngestor
from src.database.llm import create_groq_llm
from src.database.db import get_connection
from src.database.guidance.guidance_retriever import GuidanceRetriever
from src.database.sql.sql_ingestion import SQLIngester
from src.database.sql.sql_retriever import SQLRetriever
from src.database.sql.sql_store import SQLStore
from src.database.vector.vector_ingestor import VectorIngestor
from src.database.vector.vector_store import VectorStore
from src.database.vector.vector_retriever import VectorRetriever
from src.database.llm import create_vision_llm, create_google_llm
from src.database.dependencies import create_embedder
from src.database.guidance.guidance_store import GuidanceStore

from src.pipelines.retrieval_pipeline import RetrievalPipeline
from src.pipelines.scraping.scrape_ingestion_pipeline import ScrapeIngestionPipeline
from src.pipelines.vector_ingestion import VectorIngestion
from src.pipelines.answer_pipeline import AnswerPipeline
from src.pipeline import MainPipeline

# ---------- Shared resources ----------

def create_entity_store(conn):
    print("loaded entity store")
    return EntityStore(conn=conn)

def create_entity_retriever(entity_store, embedder):
    print("loaded entity retriever")
    return EntityRetriever(entity_store=entity_store, embedder=embedder)

def create_entity_ingestor(entity_store, embedder):
    print("loaded entity ingestor")
    return EntityIngestor(entity_store=entity_store, embedder=embedder)

def create_vector_store(conn):
    print("loaded vector store")
    return VectorStore(conn=conn)


def create_vector_retriever(vector_store, embedder):
    print("loaded vector retriever")
    return VectorRetriever(vector_store=vector_store, embedder=embedder)


def create_vector_ingestor(conn, vector_store):
    print("loaded vector ingestor")
    embedder = create_embedder()
    return VectorIngestor(
        vector_store=vector_store,
        embedder=embedder,
        conn=conn,
    )


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

def create_guidance_store(conn):
    print('loaded vector store')
    return GuidanceStore(conn=conn)

def create_sql_store(conn):
    return SQLStore(
        conn=conn
    )


def create_sql_retriever(guidance_retriever, sql_store, llm, embedder, entity_retriever):
    return SQLRetriever(
        guidance_retriever=guidance_retriever,
        sql_store=sql_store,
        llm=llm,
        embedder=embedder,
        entity_retriver=entity_retriever
    )

def create_sql_ingestor(sql_store):
    return SQLIngester(sql_store=sql_store)

def create_guidance_retriever(guidance_store, embedder):
    return GuidanceRetriever(
        guidance_store=guidance_store,
        embedder=embedder
    )

def create_guidance_ingestor(guidance_store, embedder):
    return GuidanceIngestor(
        guidance_store=guidance_store,
        embedder=embedder
    )



# ---------- Pipeline factories ----------

def create_vector_ingestion(vector_ingestor):
    return VectorIngestion(
        splitter=create_text_splitter(),
        ingestor=vector_ingestor,
    )


def create_answer_pipeline(llm):
    return AnswerPipeline(
        llm=llm,
    )

def create_retrieval_pipeline(vector_retriever, sql_retriever, routing_llm):
    return RetrievalPipeline(
        vector_retriever=vector_retriever,
        sql_retriever=sql_retriever,
        routing_llm=routing_llm
    )

def create_scrape_ingestion_pipeline(sql_ingestor, sql_retriever, vector_ingestor, embedder):
    return ScrapeIngestionPipeline(
        sql_ingester=sql_ingestor,
        sql_retriever=sql_retriever,
        vector_ingestor=vector_ingestor,
        embedder=embedder
    )

conn = create_connection()
llm = create_groq_llm()
embedder = create_embedder()


# ---------- App wiring ----------

def create_app() -> MainPipeline:

    entity_store = create_entity_store(conn=conn)
    entity_retriever = create_entity_retriever(entity_store=entity_store, embedder=embedder)

    # guidance
    guidance_store = create_guidance_store(conn=conn)
    guidance_retriever = create_guidance_retriever(guidance_store=guidance_store, embedder=embedder)
    guidance_ingestor = create_guidance_ingestor(guidance_store=guidance_store, embedder=embedder)

    # --- Vector infra ---
    vector_store = create_vector_store(conn=conn)
    vector_retriever = create_vector_retriever(vector_store=vector_store, embedder=embedder)
    vector_ingestor = create_vector_ingestor(conn=conn, vector_store=vector_store)

    # sql
    sql_store = create_sql_store(conn=conn)
    sql_retriever = create_sql_retriever(guidance_retriever=guidance_retriever, llm=llm, sql_store=sql_store, embedder=embedder, entity_retriever=entity_retriever)
    sql_ingestor = create_sql_ingestor(sql_store=sql_store)

    # --- Pipelines ---
    vector_ingestion = create_vector_ingestion(vector_ingestor=vector_ingestor)
    answer_pipeline = create_answer_pipeline(llm=llm)
    retrieval = create_retrieval_pipeline(vector_retriever=vector_retriever, sql_retriever=sql_retriever, routing_llm=llm)
    scrape_ingestion = create_scrape_ingestion_pipeline(sql_ingestor=sql_ingestor, sql_retriever=sql_retriever, vector_ingestor=vector_ingestor, embedder=embedder)

    return MainPipeline(
        vector_ingestion=vector_ingestion,
        scrape_ingestion=scrape_ingestion,
        answer=answer_pipeline,
        retrieval=retrieval,
        guidance_ingestor=guidance_ingestor
    )

