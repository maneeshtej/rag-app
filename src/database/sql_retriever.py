from src.models.user import User


class SQLRetriever:
    def __init__(self, sql_store, llm):
        self.sql_store = sql_store
        self.llm = llm



    def retrieve(self, query:str, user:User, k:int=5):

        return query