CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT DEFAULT 'default'
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    FOREIGN KEY(doc_id) REFERENCES documents(id) ON DELETE CASCADE
);
