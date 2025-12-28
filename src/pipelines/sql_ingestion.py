from src.models.user import User
from langchain_core.messages import HumanMessage
from src.services.extract_service import ocr_image

class SQLIngestion:
    def __init__(self, conn, llm, vision_llm):
        self.conn = conn
        self.llm = llm
        self.vision_llm = vision_llm

    def run(self, path: str, user: User):
        return ocr_image(path=path)