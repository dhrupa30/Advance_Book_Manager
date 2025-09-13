import sqlite3
import os
import bcrypt

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "books.db")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -------------------------------
# Users
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash BLOB NOT NULL,
    role TEXT NOT NULL
)
""")

# -------------------------------
# Authors
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS authors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    bio TEXT
)
""")

# -------------------------------
# Categories
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# -------------------------------
# Books
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER REFERENCES authors(id),
    category_id INTEGER REFERENCES categories(id),
    status TEXT,
    cover_image TEXT,
    summary TEXT,
    publisher TEXT,
    language TEXT
)
""")

# -------------------------------
# Many-to-many joins
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS book_authors(
    book_id INTEGER,
    author_id INTEGER,
    PRIMARY KEY(book_id, author_id),
    FOREIGN KEY(book_id) REFERENCES books(id),
    FOREIGN KEY(author_id) REFERENCES authors(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS book_categories(
    book_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY(book_id, category_id),
    FOREIGN KEY(book_id) REFERENCES books(id),
    FOREIGN KEY(category_id) REFERENCES categories(id)
)
""")

# -------------------------------
# User ↔ Book Status
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_book_status(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('unread','reading','completed','on_hold','dropped')),
    progress_percent INTEGER DEFAULT 0 CHECK (progress_percent BETWEEN 0 AND 100),
    current_page INTEGER,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    notes TEXT,
    started_at TEXT,
    finished_at TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id),
    UNIQUE(user_id, book_id)
)
""")

# -------------------------------
# FTS5 Search Table
# -------------------------------
cursor.execute("""
CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(
    title, summary, publisher, language, content='books', content_rowid='id'
)
""")

# -------------------------------
# Default data
# -------------------------------
# Admin user
cursor.execute("SELECT * FROM users WHERE username='admin'")
if not cursor.fetchone():
    password = "admin"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                   ("admin", hashed_password, "admin"))

# Default author
cursor.execute("SELECT * FROM authors WHERE name='Default Author'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO authors (name, bio) VALUES (?, ?)",
                   ("Default Author", "This is a placeholder author."))

# Default category
cursor.execute("SELECT * FROM categories WHERE name='Default Category'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO categories (name) VALUES (?)", ("Default Category",))

# Commit + close
conn.commit()
conn.close()
print("📚 Database setup completed successfully.")
