from langchain_core.documents import Document


class Reranker:

    def __init__(self, embedder, llm):
        self.embedder = embedder
        self.llm = llm

    def run(self, query:str, docs:list[Document]) -> list[Document]:
        raise NotImplementedError