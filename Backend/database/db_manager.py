import sqlite3
import os

DB_PATH = "database.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_connection()
    c = conn.cursor()
    with open(schema_path, "r") as f:
        c.executescript(f.read())
    conn.commit()
    conn.close()

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    
    result = None
    if fetch_one:
        result = c.fetchone()
    elif fetch_all:
        result = c.fetchall()
        
    conn.commit()
    lastrowid = c.lastrowid
    conn.close()
    
    return result if (fetch_one or fetch_all) else lastrowid

def insert_document(filename, user_id="default"):
    return execute_query(
        "INSERT INTO documents (filename, status, user_id) VALUES (?, ?, ?)",
        (filename, 'pending', user_id)
    )

def update_document_status(doc_id, status):
    execute_query("UPDATE documents SET status = ? WHERE id = ?", (status, doc_id))

def insert_chunk(doc_id, text, chunk_index):
    return execute_query(
        "INSERT INTO chunks (doc_id, text, chunk_index) VALUES (?, ?, ?)",
        (doc_id, text, chunk_index)
    )

def get_all_chunks():
    # Returns [(id, text, filename)]
    return execute_query(
        "SELECT c.id, c.text, d.filename FROM chunks c JOIN documents d ON c.doc_id = d.id",
        fetch_all=True
    )

def get_chunk_by_id(chunk_id):
    return execute_query(
        "SELECT c.text, d.filename FROM chunks c JOIN documents d ON c.doc_id = d.id WHERE c.id = ?",
        (chunk_id,), fetch_one=True
    )
