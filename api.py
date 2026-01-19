# api.py
import os
from flask import Flask, request, jsonify
from src.services.user_service import create_user, user_login
from src.models.user import User
from uuid import uuid4

from main_pipeline_setup import build_app

rag_app, conn, get_loader = build_app()

api = Flask(__name__)

from flask import request

UPLOAD_DIR = "/tmp/rag_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

import json
from pathlib import Path

SESSION_FILE = Path("/tmp/rag_user.json")

def save_user(user):
    SESSION_FILE.write_text(json.dumps({
        "id": str(user.id),
        "username": user.username,
        "role": user.role,
        "access_level": user.access_level,
    }))

def load_user():
    if not SESSION_FILE.exists():
        return None
    return json.loads(SESSION_FILE.read_text())



@api.post("/ingest")
def ingest():
    file = request.files.get("file")
    username = request.form.get("username")

    if not file or not username:
        return jsonify({"error": "file and username required"}), 400

    user = user_login(username=username, conn=conn)
    if not user:
        return jsonify({"error": "invalid user"}), 401

    path = os.path.join(UPLOAD_DIR, f"{uuid4()}_{file.filename}")
    file.save(path)

    loader = get_loader(path)

    try:
        result = rag_app.ingest_vector(loader=loader, user=user)
        conn.commit()
        return jsonify({"status": "ok", "chunks": result})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(path):
            os.remove(path)


@api.post("/query")
def query():
    data = request.json
    question = data["query"]

    user_data = load_user()
    if not user_data:
        return jsonify({"error": "not logged in"}), 401

    user = User(
        id=user_data["id"],
        username=user_data["username"],
        role=user_data["role"],
        access_level=user_data["access_level"],
    )

    result = rag_app.vector_inference(
        query=question,
        user=user,
    )

    return jsonify(result)


@api.post("/signup")
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")  # placeholder for now

    if not username:
        return jsonify({"error": "username required"}), 400

    try:
        user = create_user(
            username=username,
            role="user",
            access_level=1,
            conn=conn,
        )
        conn.commit()
        return jsonify({
            "id": str(user.id),
            "username": user.username,
            "role": user.role,
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    


@api.post("/login")
def login():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "username required"}), 400

    user = user_login(username=username, conn=conn)
    if not user:
        return jsonify({"error": "invalid user"}), 401

    save_user(user)

    return jsonify({
        "id": str(user.id),
        "username": user.username,
        "role": user.role,
        "access_level": user.access_level,
    })





if __name__ == "__main__":
    api.run(debug=True)
