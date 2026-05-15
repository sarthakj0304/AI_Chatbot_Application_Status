import os
from dotenv import load_dotenv

# Load env variables first
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Import our new modules
from database.db_manager import init_db, execute_query

# ==============================
# Initialize Database (Must happen before service imports)
# ==============================
print("🔹 Initializing SQLite Database Schema...")
init_db()

from services.ingestion_service import handle_upload
from services.generation_service import generation_service

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# ==============================
# Persistent Leads Database
# ==============================

def init_leads_db():
    conn = sqlite3.connect("leads.db", check_same_thread=False)
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
# Document Upload Endpoint
# ==============================
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    response, status_code = handle_upload(file)
    return jsonify(response), status_code

@app.route("/admin/documents", methods=["GET"])
def get_documents():
    docs = execute_query("SELECT id, filename, status, upload_time FROM documents ORDER BY id DESC", fetch_all=True)
    result = [{"id": d[0], "filename": d[1], "status": d[2], "upload_time": d[3]} for d in docs]
    return jsonify(result)

# ==============================
# Chat Endpoint
# ==============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"answer": "No query provided."}), 400

    # Use the new generation service (which uses retrieval_service internally)
    result = generation_service.generate_answer(query)
    answer = result["answer"]
    citations = result["citations"]

    cursor = conversation_conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (query, answer) VALUES (?, ?)",
        (query, answer)
    )
    conversation_conn.commit()

    return jsonify({"answer": answer, "citations": citations})

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
    cursor = conversation_conn.cursor()
    cursor.execute("""
        SELECT query, answer, timestamp
        FROM conversations
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    return jsonify(rows)

# ==============================
# Admin - Most Asked Questions
# ==============================
@app.route("/admin/stats", methods=["GET"])
def admin_stats():
    cursor = conversation_conn.cursor()
    cursor.execute("""
        SELECT query, COUNT(*) as count
        FROM conversations
        GROUP BY query
        ORDER BY count DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    return jsonify(rows)

# ==============================
# Admin - Analytics
# ==============================
@app.route("/admin/analytics", methods=["GET"])
def admin_analytics():
    cursor = conversation_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE answer LIKE '%don''t have the specific context%'")
    unanswered = cursor.fetchone()[0]
    
    return jsonify({
        "total_queries": total,
        "unanswered_queries": unanswered,
        "success_rate": round(((total - unanswered) / total * 100) if total > 0 else 100, 2)
    })

# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)