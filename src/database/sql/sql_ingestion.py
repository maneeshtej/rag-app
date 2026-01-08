class SQLIngester:
    def __init__(self, sql_store):
        self.sql_store = sql_store

    def truncate_tables(self, *, tables: list[str]):
        return self.sql_store.truncate_tables(tables=tables)

    def ingest(self, *, sql_obj: dict, test: bool = False):
        if sql_obj["action"] == "insert":
            cols = ", ".join(sql_obj["data"].keys())
            vals = ", ".join(["%s"] * len(sql_obj["data"]))
            sql = f"INSERT INTO {sql_obj['table']} ({cols}) VALUES ({vals})"

            if sql_obj.get("returning"):
                sql += f" RETURNING {sql_obj['returning']}"

            params = tuple(sql_obj["data"].values())

            if test:
                return sql, params

            return self.sql_store.execute_write(sql, params)

        raise ValueError("Unsupported action")
