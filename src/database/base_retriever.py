class BaseRetriver:

    def __init__(self, vector_retriever, sql_retriever):
        self.vector_retriver = vector_retriever
        self.sql_retriver = sql_retriever