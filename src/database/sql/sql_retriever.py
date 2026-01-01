from src.models.user import User
from src.schema.schema import SCHEMA_MAP, SCHEMA_EXTENSION


class SQLRetriever:
    def __init__(self, sql_store, llm, guidance_store):
        self.sql_store = sql_store
        self.llm = llm
        self.guidance_store = guidance_store

    def _get_related_schema(self, *, query:str, user:User, k:int=5):
        related_tables = self.guidance_store.retrieve(
            query=query,
            user=user,
            k=k,
            type="table"
        )

        related_schema = {
            name: SCHEMA_MAP[name] 
            for table in related_tables
            if (name := table.metadata.get("table_name")) in SCHEMA_MAP
        }

        existing_tables = set(related_schema.keys())
        print(existing_tables)

        for table_name in existing_tables:
            for ext_table_name in SCHEMA_EXTENSION.get(table_name, []):
                if ext_table_name not in existing_tables and ext_table_name in SCHEMA_MAP:
                    related_schema[ext_table_name] = SCHEMA_MAP[ext_table_name]

        print(related_schema.keys())


        return related_schema

    def retrieve(self, *, query:str, user:User, k:int=5):
        related_schema = self._get_related_schema(query=query, user=user, k=5)
        return related_schema