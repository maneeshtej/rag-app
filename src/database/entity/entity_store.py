from psycopg import Connection
from typing import Iterable, Sequence


class EntityStore:
    def __init__(self, conn: Connection):
        self.conn = conn

    def execute_read(
        self,
        sql: str,
        params: Sequence | None = None,
    ) -> list:
        """
        Execute a SELECT query.
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def execute_write(
        self,
        sql: str,
        params: Sequence | Iterable[Sequence] | None = None,
    ) -> int:
        """
        Execute INSERT / UPDATE / DELETE.

        params:
        - None                 -> execute(sql)
        - tuple / sequence     -> execute(sql, params)
        - iterable of tuples   -> executemany(sql, params)
        """
        with self.conn.cursor() as cur:
            if params is None:
                cur.execute(sql)
                return cur.rowcount

            if isinstance(params, (list, tuple)) and params and isinstance(params[0], (list, tuple)):
                # bulk
                cur.executemany(sql, params)
                return cur.rowcount

            # single
            cur.execute(sql, params)
            return cur.rowcount
