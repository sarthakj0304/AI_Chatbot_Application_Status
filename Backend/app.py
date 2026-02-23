from flask import Flask, request, jsonify
from RAG.src.search import RAGSearch
import time
from flask_cors import CORS

import sqlite3

# Persistent DB for leads
def init_leads_db():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            role TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# In-memory DB for conversations
conversation_conn = sqlite3.connect(":memory:", check_same_thread=False)
conversation_cursor = conversation_conn.cursor()

conversation_cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        answer TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

init_leads_db()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
print("🔹 Loading RAG system...")
rag = RAGSearch("RAG/faiss_store")
print(" RAG ready.")

# In-memory conversation logs
conversation_logs = []
query_counts = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query")

    answer = rag.search(query)

    conversation_cursor.execute(
        "INSERT INTO conversations (query, answer) VALUES (?, ?)",
        (query, answer)
    )
    conversation_conn.commit()

    return jsonify({"answer": answer})


@app.route("/lead", methods=["POST"])
def lead():
    data = request.json
    email = data.get("email")
    role = data.get("role")

    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO leads (email, role) VALUES (?, ?)",
        (email, role),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Lead captured successfully"})


@app.route("/admin/logs", methods=["GET"])
def admin_logs():
    conversation_cursor.execute("""
        SELECT query, answer, timestamp
        FROM conversations
        ORDER BY id DESC
    """)

    rows = conversation_cursor.fetchall()

    return jsonify(rows)


@app.route("/admin/stats", methods=["GET"])
def admin_stats():
    conversation_cursor.execute("""
        SELECT query, COUNT(*) as count
        FROM conversations
        GROUP BY query
        ORDER BY count DESC
        LIMIT 5
    """)

    rows = conversation_cursor.fetchall()

    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)