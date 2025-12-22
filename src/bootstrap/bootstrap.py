from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.vectorstore import create_vectorstore, create_embedder
from database.db import get_connection
from database.pg_vectorstore import PGVectorStore
from database.pg_retrieval import PGRetriever
from database.llm import create_llm
from pipeline import MainPipeline
from pipelines.ingestion_pipeline import IngestionPipeline
from pipelines.retrieval_pipeline import RetrievalPipeline
from pipelines.answer_pipeline import AnswerPipeline

def create_ingestion_app():
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=500,
        chunk_overlap=50,
    )
    embedder = create_embedder()
    conn = get_connection()
    vectorstore = PGVectorStore(embedder=embedder, conn=conn)

    ingestion = IngestionPipeline(splitter=splitter, vectorstore=vectorstore)
  

    return ingestion

def create_retrival_app(k:int = 5):
    embedder = create_embedder()
    conn = get_connection()
    vectorstore: PGVectorStore = PGVectorStore(embedder=embedder, conn=conn)

    retriever: PGRetriever = PGRetriever(vectorstore=vectorstore, embedder=embedder)

    return(
        RetrievalPipeline(retriever=retriever)
    )

def create_answer_app():
    llm = create_llm()
    answer: AnswerPipeline = AnswerPipeline(llm=llm)

    return answer



def create_app():
    app: MainPipeline = MainPipeline(
        ingestion=create_ingestion_app(),
        retriever=create_retrival_app(),
        answer=create_answer_app()
        )

    return app

