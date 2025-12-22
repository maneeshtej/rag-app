from multiprocessing import connection
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dbname="rag_app",
        user="postgres",
        password="12345",
        host="localhost",
        port=5432,
    )