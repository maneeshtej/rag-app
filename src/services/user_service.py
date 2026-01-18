import uuid
from src.database.db import get_connection
from src.models.user import User

def create_user(
        username: str,
        role: str,
        access_level: int,
        conn
):
    user_id = uuid.uuid4()

    query = """
    INSERT INTO users(id, username, role, access_level)
    values(%s, %s, %s, %s)
    RETURNING id, username, role, access_level;
    """


    with conn.cursor() as cur:
        cur.execute(query, (str(user_id), username, role, access_level))
        row = cur.fetchone()
        conn.commit()

    return User(
        id=row[0],
        username=row[1],
        role=row[2],
        access_level=row[3]
    )

def user_login(username: str, conn):
    
    
    query = """
    SELECT id, username, role, access_level FROM users
    WHERE username = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (username, ))
        row = cur.fetchone()
        conn.commit()

    if row == None:
        return None
        
    return User(
        id=row[0],
        username=row[1],
        role=row[2],
        access_level=row[3]
    )