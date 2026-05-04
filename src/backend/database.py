"""
Module: database.py
Author: Shivranjini Pandey 
Date: 2026-04-12

Description:
This module manages the database connection and operations for the cinema system.
It is responsible for creating tables, initializing data, and executing queries.
"""
import sqlite3
from datetime import datetime, timedelta
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

    db.exec("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id      INTEGER NOT NULL UNIQUE,
        amount          REAL NOT NULL,
        payment_method  TEXT NOT NULL CHECK(payment_method IN ('CARD','CASH','UPI')),
        card_last4      TEXT,
        transaction_ref TEXT NOT NULL UNIQUE,
        status          TEXT NOT NULL CHECK(status IN ('SUCCESS','FAILED','REFUNDED')),
        paid_at         TEXT NOT NULL,
        FOREIGN KEY(booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
    )
""")
    # always call seed after tables exist
    seed_if_empty(db)

def seed_if_empty(db: DB):
    # ── Manager account ─────────────────────────────────
    if not db.query("SELECT 1 FROM users WHERE email=?",
                    ("manager@cinema.com",)):
        db.exec(
            "INSERT INTO users(name,email,password_hash,role,created_at)"
            " VALUES(?,?,?,?,?)",
            ("Manager", "manager@cinema.com",
             sha256("manager123"), "manager", now_iso())
        )

    # ── Movies ──────────────────────────────────────────
    if not db.query("SELECT 1 FROM movies LIMIT 1"):
        movies = [
            ("Interstellar",          "Sci-Fi",       "English",  169,
             "In a future where Earth is becoming uninhabitable, a former pilot "
             "joins a mission to travel beyond our galaxy in search of a new home "
             "for humanity. As the journey pushes the limits of time and space, "
             "the crew must confront impossible choices and the true cost of survival."),

            ("Arrival",               "Sci-Fi",       "English",  116,
             "When mysterious spacecraft appear around the world, a linguist is "
             "recruited to communicate with the unknown visitors. As she works to "
             "understand their language, the line between past, present, and future "
             "begins to blur."),

            ("Hacksaw Ridge",         "War/Drama",    "English",  139,
             "Desmond Doss, a deeply religious young man, enlists in the U.S. Army "
             "during World War II but refuses to carry a weapon. His beliefs are put "
             "to the ultimate test when he is sent into one of the war's deadliest battles."),

            ("Across the Spiderverse","Animation",    "English",  140,
             "Miles Morales reunites with Gwen Stacy and is pulled into a vast "
             "multiverse of Spider-People. When he encounters a powerful new threat, "
             "Miles must redefine what it means to be a hero."),

            ("The Maze Runner",       "Action",       "English",  113,
             "A teenage boy wakes up in a mysterious glade surrounded by a massive "
             "ever-changing maze with no memory of his past. He becomes determined "
             "to uncover the maze's secrets and find a way out."),

            ("Howl's Moving Castle",  "Animation",    "Japanese", 119,
             "A young woman named Sophie is transformed into an old woman and seeks "
             "refuge in the magical moving castle of the wizard Howl. As she navigates "
             "a world of war and enchantment, she discovers that nothing is quite "
             "what it seems."),
        ]

        for title, genre, language, duration, synopsis in movies:
            db.exec(
                "INSERT INTO movies(title,genre,language,duration_min,synopsis)"
                " VALUES(?,?,?,?,?)",
                (title, genre, language, duration, synopsis)
            )

    # ── Theatres ─────────────────────────────────────────
    if not db.query("SELECT 1 FROM theatres LIMIT 1"):
        db.exec(
            "INSERT INTO theatres(name,city,address) VALUES(?,?,?)",
            ("Downtown Cinema", "Los Angeles", "123 Main St")
        )
        db.exec(
            "INSERT INTO theatres(name,city,address) VALUES(?,?,?)",
            ("Westside Multiplex", "Santa Monica", "456 Ocean Ave")
        )

    # ── Screens ──────────────────────────────────────────
    if not db.query("SELECT 1 FROM screens LIMIT 1"):
        theatres = db.query("SELECT theatre_id FROM theatres")
        for theatre in theatres:
            tid = theatre["theatre_id"]
            db.exec(
                "INSERT INTO screens(theatre_id,name,rows,cols)"
                " VALUES(?,?,?,?)",
                (tid, "Screen 1", 6, 8)
            )
            db.exec(
                "INSERT INTO screens(theatre_id,name,rows,cols)"
                " VALUES(?,?,?,?)",
                (tid, "Screen 2", 5, 7)
            )

    # ── Shows ────────────────────────────────────────────
    if not db.query("SELECT 1 FROM shows LIMIT 1"):
        movies  = db.query("SELECT movie_id FROM movies")
        screens = db.query("SELECT screen_id FROM screens")

        # Fixed showtimes
        fixed_times = ["14:00:00", "17:30:00", "20:30:00"]
        prices = [12.0, 14.0, 16.0]

        today = datetime.now().date()
        days = [today, today + timedelta(days=1)]  # today + tomorrow

        for movie in movies:
            for screen in screens:
                for day in days:
                    for time_str, price in zip(fixed_times, prices):
                        show_datetime = f"{day} {time_str}"

                        db.exec(
                            """
                            INSERT INTO shows(movie_id, screen_id, show_datetime, base_price)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                movie["movie_id"],
                                screen["screen_id"],
                                show_datetime,
                                price
                            )
                        )
                    