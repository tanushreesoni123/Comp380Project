import sqlite3
from src.backend.database import DB
from src.utils import sha256, now_iso
"""
a) Module/Class Name: AuthService (Authentication Service Layer)

b) Date: April 7, 2026

c) Programmer: Shivranjini Pandey

d) Description:
This module handles user authentication functionalities including user registration and login.
It interacts with the database through the DB class and ensures secure handling of user credentials
using hashing.

e) Important Functions:

1. register(name: str, email: str, password: str) -> tuple[bool, str]
- Input:
• name (str): User's name
• email (str): User's email
• password (str): User's password
- Output:
• (bool, str): Returns a tuple where:
- bool indicates success or failure
- str provides a message ("Registered successfully." or error message)
- Description:
Validates input fields, hashes the password, and inserts a new user into the database.
Handles duplicate email cases using exception handling.

2. login(email: str, password: str)
- Input:
• email (str): User's email
• password (str): User's password
- Output:
• Returns user record (sqlite3.Row) if credentials are valid, otherwise None
- Description:
Verifies user credentials by comparing hashed password with stored value in database.

f) Important Data Structures:
- Uses SQLite database rows (sqlite3.Row) to represent user records.
- Passwords are stored as hashed strings using SHA-256 for security.

g) Algorithm/Design Choices:
- Password hashing (SHA-256) is used instead of plain text storage for security reasons.
- Input validation ensures required fields are provided before database operations.
- Exception handling (IntegrityError) is used to manage duplicate email entries efficiently.
- Simple query-based authentication is chosen for performance and simplicity over more complex authentication mechanisms.
"""
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
        