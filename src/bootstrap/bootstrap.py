from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.database.dependencies import create_vectorstore, create_embedder
from src.database.db import get_connection
from src.database.vector_store import VectorStore
from src.database.vector_retrieval import VectorRetriever
from src.database.llm import create_llm, create_vision_llm
from src.pipeline import MainPipeline
from src.pipelines.vector_ingestion import VectorIngestion
from src.pipelines.vector_retrieval import VectorRetrieval
from src.pipelines.answer_pipeline import AnswerPipeline
from src.pipelines.sql_ingestion import SQLIngestion

def create_vector_ingestion_app():
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=500,
        chunk_overlap=50,
    )
    embedder = create_embedder()
    conn = get_connection()
    vectorstore = VectorStore(embedder=embedder, conn=conn)

    ingestion = VectorIngestion(splitter=splitter, vectorstore=vectorstore)
  

    return ingestion

def create_sql_ingestion_app():
    conn = get_connection()
    llm = create_llm()
    vision_llm = create_vision_llm()

    sql_ingestion: SQLIngestion = SQLIngestion(conn=conn, llm=llm, vision_llm=vision_llm)

    return sql_ingestion

def create_retrival_app(k:int = 5):
    embedder = create_embedder()
    conn = get_connection()
    vectorstore: VectorStore = VectorStore(embedder=embedder, conn=conn)

    retriever: VectorRetriever = VectorRetriever(vectorstore=vectorstore, embedder=embedder)

    return(
        VectorRetrieval(retriever=retriever)
    )

def create_answer_app():
    llm = create_llm()
    answer: AnswerPipeline = AnswerPipeline(llm=llm)

    return answer

def create_vector_store():
    embedder = create_embedder()
    conn = get_connection()
    vector_store = VectorStore(
        embedder=embedder,
        conn=conn
    )
    return vector_store


def create_app():
    app: MainPipeline = MainPipeline(
        vector_ingestion=create_vector_ingestion_app(),
        vector_retriever=create_retrival_app(),
        answer=create_answer_app(),
        sql_ingestion=create_sql_ingestion_app(),
        vector_store=create_vector_store()
        )

    return app



