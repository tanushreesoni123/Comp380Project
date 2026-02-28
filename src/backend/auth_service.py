import sqlite3
from src.backend.database import DB
from src.backend.utils import sha256, now_iso

class AuthService:
    def __init__(self, db: DB):
        self.db = db

    def register(self, name: str, email: str, password: str) -> tuple[bool, str]:
        if not name or not email or not password:
            return False, "All fields required."
        try:
            self.db.exec(
                "INSERT INTO users(name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, email.strip().lower(), sha256(password), "customer", now_iso())
            )
            return True, "Registered successfully."
        except sqlite3.IntegrityError:
            return False, "Email already exists."

    def login(self, email: str, password: str):
        rows = self.db.query(
            "SELECT user_id, name, email, role FROM users WHERE email=? AND password_hash=?",
            (email.strip().lower(), sha256(password))
        )
        return rows[0] if rows else None
        