import sqlite3
from src.utils import sha256, now_iso

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

    db.exec("""
        CREATE TABLE IF NOT EXISTS cart (
            cart_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            show_id    INTEGER NOT NULL,
            seat_label TEXT NOT NULL,
            added_at   TEXT NOT NULL,
            UNIQUE(user_id, show_id, seat_label),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY(show_id) REFERENCES shows(show_id) ON DELETE CASCADE
        )
    """)

    db.exec("""
    CREATE TABLE IF NOT EXISTS movies (
        movie_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        title        TEXT NOT NULL,
        genre        TEXT,
        language     TEXT,
        duration_min INTEGER,
        synopsis     TEXT
    )
    """)

    db.exec("""
    CREATE TABLE IF NOT EXISTS theatres (
        theatre_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        city       TEXT,
        address    TEXT
    )
    """)

    db.exec("""
    CREATE TABLE IF NOT EXISTS screens (
        screen_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        theatre_id INTEGER NOT NULL,
        name       TEXT NOT NULL,
        rows       INTEGER NOT NULL,
        cols       INTEGER NOT NULL,
        FOREIGN KEY(theatre_id) REFERENCES theatres(theatre_id) ON DELETE CASCADE
    )
    """)

    db.exec("""
    CREATE TABLE IF NOT EXISTS shows (
        show_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id      INTEGER NOT NULL,
        screen_id     INTEGER NOT NULL,
        show_datetime TEXT NOT NULL,
        base_price    REAL NOT NULL,
        FOREIGN KEY(movie_id)  REFERENCES movies(movie_id)  ON DELETE CASCADE,
        FOREIGN KEY(screen_id) REFERENCES screens(screen_id) ON DELETE CASCADE
    )
    """)

    db.exec("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        show_id      INTEGER NOT NULL,
        booking_time TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status       TEXT NOT NULL CHECK(status IN ('CONFIRMED','CANCELED')),
        cancel_time  TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(show_id) REFERENCES shows(show_id) ON DELETE CASCADE
    )
    """)

    db.exec("""
    CREATE TABLE IF NOT EXISTS booking_seats (
        booking_seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id      INTEGER NOT NULL,
        seat_label      TEXT NOT NULL,
        seat_price      REAL NOT NULL,
        UNIQUE(booking_id, seat_label),
        FOREIGN KEY(booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
    )
    """)

    db.exec("""
    CREATE TABLE IF NOT EXISTS cart (
        cart_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        show_id    INTEGER NOT NULL,
        seat_label TEXT NOT NULL,
        added_at   TEXT NOT NULL,
        UNIQUE(user_id, show_id, seat_label),
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(show_id) REFERENCES shows(show_id) ON DELETE CASCADE
    )
    """)

