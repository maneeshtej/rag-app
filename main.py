from pathlib import Path
from uuid import UUID, uuid4
import psycopg2
from src.database.dependencies import create_embedder
from src.database.llm import create_google_llm
from src.database.vector.vector_ingestor import VectorIngestor
from src.database.vector.vector_reranker import DeterministicReranker
from src.database.vector.vector_retriever import VectorRetriever
from src.database.vector.vector_store import VectorStore
from src.models.user import User
from src.pipeline import MainPipeline
from src.pipelines.inference.answer_generator import AnswerGenerator
from src.pipelines.vector.vector_ingestion import VectorIngestion
from src.pipelines.vector.vetor_retrieval import VectorRetrieval
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.services.user_service import create_user, user_login

llm = create_google_llm()
embedder = create_embedder()
def create_text_splitter():
    print('loaded splitter')
    return RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=500,
        chunk_overlap=50,
    )
splitter = RecursiveCharacterTextSplitter()
conn = psycopg2.connect(
        dbname="rag_test",
        user="postgres",
        password="12345",
        host="localhost",
        port=5432,
    )
system_user = User(
    id=uuid4(),
    username="Maneesh",
    role="admin",
    access_level=0
)
splitter = create_text_splitter()
vector_store = VectorStore(conn=conn)
retriever = VectorRetriever(vector_store=vector_store)
vector_ingestor = VectorIngestor(embedder=embedder, vector_store=vector_store)
vector_ingestion = VectorIngestion(splitter=splitter, vector_ingestor=vector_ingestor)
reranker = DeterministicReranker()
answer = AnswerGenerator(llm=llm)
vector_retrieval = VectorRetrieval(retriever=retriever, reranker=reranker, embedder=embedder)
app = MainPipeline(
    answer=answer,
    vector_retrieval=vector_retrieval,
    vector_ingestion=vector_ingestion
)

def get_loader(path: str):
    ext = Path(path).suffix.lower()

    if ext == ".pdf":
        return PyPDFLoader(path)

    if ext in {".txt", ".md"}:
        return TextLoader(path, encoding="utf-8")

    raise ValueError(f"Unsupported file type: {ext}")

if __name__ == "__main__":
    loader = get_loader(path="test.txt")
    user = None
    try:
        # user = create_user(username="maneesh", role="admin", access_level=0, conn=conn)
        user = user_login(username="maneesh", conn=conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    
    # if user:
    #     try:
    #         output = app.ingest_vector(loader=loader, user=user)
    #         conn.commit()
    #     except Exception as e:
    #         conn.rollback()
    #         raise e
    output = app.vector_inference(query="what is langchain", user=system_user)
    print(output)