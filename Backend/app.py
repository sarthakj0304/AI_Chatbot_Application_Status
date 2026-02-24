from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from RAG.search import RAGSearch

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# ==============================
# Load RAG once (VERY IMPORTANT)
# ==============================
print("🔹 Loading RAG system...")
rag = RAGSearch("rag/faiss_store")
print(" RAG ready.")

# ==============================
# Persistent Leads Database
# ==============================

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

init_leads_db()

# ==============================
# In-Memory Conversations DB
# (clears when server restarts)
# ==============================

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

# ==============================
# Chat Endpoint
# ==============================

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"answer": "No query provided."}), 400

    answer = rag.search(query)

    conversation_cursor.execute(
        "INSERT INTO conversations (query, answer) VALUES (?, ?)",
        (query, answer)
    )
    conversation_conn.commit()

    return jsonify({"answer": answer})


# ==============================
# Lead Capture Endpoint
# ==============================

@app.route("/lead", methods=["POST"])
def lead():
    data = request.json
    email = data.get("email")
    role = data.get("role")

    if not email or not role:
        return jsonify({"message": "Missing email or role"}), 400

    conn = sqlite3.connect("leads.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO leads (email, role) VALUES (?, ?)",
        (email, role)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Lead captured successfully"})


# ==============================
# Admin - Conversation Logs
# ==============================

@app.route("/admin/logs", methods=["GET"])
def admin_logs():
    conversation_cursor.execute("""
        SELECT query, answer, timestamp
        FROM conversations
        ORDER BY id DESC
    """)

    rows = conversation_cursor.fetchall()
    return jsonify(rows)


# ==============================
# Admin - Most Asked Questions
# ==============================

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


# ==============================
# Run App
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)