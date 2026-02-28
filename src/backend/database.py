import sqlite3
from src.backend.utils import sha256, now_iso

class DB:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row

    def exec(self, sql: str, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def query(self, sql: str, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def close(self):
        self.conn.close()


def init_db(db: DB):
    db.exec("""
    CREATE TABLE IF NOT EXISTS users (
        user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT    NOT NULL,
        email         TEXT    NOT NULL UNIQUE,
        password_hash TEXT    NOT NULL,
        role          TEXT    NOT NULL CHECK(role IN ('customer', 'manager')),
        created_at    TEXT    NOT NULL
    )
    """)

    existing = db.query("SELECT 1 FROM users WHERE email=?", ("manager@cinema.com",))
    if not existing:
        db.exec(
            "INSERT INTO users(name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Manager", "manager@cinema.com", sha256("manager123"), "manager", now_iso())
        )