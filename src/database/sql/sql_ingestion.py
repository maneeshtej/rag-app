class SQLIngestion:
    def __init__(self, *, llm, vision_llm):
        self.llm = llm
        self.vision_llm = vision_llm

    def ingest(self):
        raise NotImplementedError