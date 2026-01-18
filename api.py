# api.py
from flask import Flask, request, jsonify
from src.services.user_service import user_login
from src.models.user import User
from uuid import uuid4

from main_pipeline_setup import build_app

rag_app, conn, get_loader = build_app()

api = Flask(__name__)

@api.post("/ingest")
def ingest():
    data = request.json
    path = data["path"]
    username = data["username"]

    user = user_login(username=username, conn=conn)
    loader = get_loader(path)

    try:
        result = rag_app.ingest_vector(loader=loader, user=user)
        conn.commit()
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500


@api.post("/query")
def query():
    data = request.json
    question = data["query"]

    # temp system user
    system_user = User(
        id=uuid4(),
        username="system",
        role="admin",
        access_level=0,
    )

    result = rag_app.vector_inference(
        query=question,
        user=system_user,
    )

    return jsonify(result)


if __name__ == "__main__":
    api.run(debug=True)
