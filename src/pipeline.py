from depreciated.vector_retrieval import VectorRetrieval
from src.models import user
from src.models.user import User
from src.pipelines.answer_pipeline import AnswerPipeline
from src.pipelines.inference.answer_generator import AnswerGenerator
from src.pipelines.vector.vector_ingestion import VectorIngestion
from src.services.user_service import create_user, user_login


class MainPipeline:
    def __init__(
        self,
        *,
        vector_ingestion,
        vector_retrieval,
        answer,
    ):
        self.vector_ingestion:VectorIngestion = vector_ingestion
        self.vector_retrieval:VectorRetrieval = vector_retrieval
        self.answer:AnswerGenerator = answer

    # ---------- INGESTION ----------

    def ingest_vector(self, loader, user: User):
        if not user:
            print("No user")
            return
        if not self.vector_ingestion:
            raise ValueError("Vector ingestion is not configured")

        return self.vector_ingestion.run(loader, user)

    # ---------- VECTOR INFERENCE ----------

    def vector_inference(
        self,
        *,
        query: str,
        user: User,
        k: int = 5,
        test: bool = False,
    ):
        if not user:
            print("No user")
            return
        if not self.vector_retrieval or not self.answer:
            raise ValueError("Vector inference pipeline is not fully configured")

        # 1. retrieve vector chunks
        chunks = self.vector_retrieval.retrieve(
            query=query,
            user=user,
            k=k,
        )

        if test:
            return chunks

        # 2. generate answer
        return self.answer.generate(
            query=query,
            chunks=chunks,
        )
