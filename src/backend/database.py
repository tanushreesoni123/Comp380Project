import sqlite3
from datetime import datetime, timedelta
from src.utils import sha256, now_iso
"""
a) Module/Class Name:
   Database Module (DB Class and Initialization Functions)

b) Date: April 12, 2026

c) Programmer: Shivranjini Pandey

d) Description:
   This module manages all database-related operations for the application.
   It establishes a connection to the SQLite database, executes SQL queries,
   and initializes the database schema. It also seeds the database with initial
   data such as users, movies, theatres, screens, and showtimes.

e) Important Functions:

   1. DB.__init__(path: str)
      - Input:
        • path (str): File path to the SQLite database
      - Output:
        • Initializes database connection
      - Description:
        Creates a connection to the SQLite database, enables foreign key constraints,
        and sets row format to sqlite3.Row for easy column access.

   2. DB.exec(sql: str, params=())
      - Input:
        • sql (str): SQL command (INSERT, UPDATE, CREATE, etc.)
        • params (tuple): Parameters for SQL query
      - Output:
        • Cursor object
      - Description:
        Executes SQL commands that modify the database and commits changes.

   3. DB.query(sql: str, params=())
      - Input:
        • sql (str): SQL SELECT query
        • params (tuple): Parameters for SQL query
      - Output:
        • List of sqlite3.Row objects
      - Description:
        Executes SELECT queries and returns results.

   4. DB.close()
      - Input: None
      - Output: None
      - Description:
        Closes the database connection.

   5. init_db(db: DB)
      - Input:
        • db (DB): Database instance
      - Output: None
      - Description:
        Creates all required tables (users, movies, theatres, screens, shows,
        bookings, booking_seats, cart) if they do not exist, and calls seed_if_empty.

   6. seed_if_empty(db: DB)
      - Input:
        • db (DB): Database instance
      - Output: None
      - Description:
        Inserts initial data into the database (manager account, movies, theatres,
        screens, and showtimes) only if the tables are empty.

f) Important Data Structures:
   - SQLite database tables (users, movies, theatres, screens, shows, bookings, booking_seats, cart).
   - sqlite3.Row objects for structured access to query results.
   - Lists and tuples for batch data insertion (e.g., movies list).

g) Algorithm/Design Choices:
   - Relational database design with foreign keys ensures data integrity and consistency.
   - Use of AUTOINCREMENT primary keys for unique identification of records.
   - Conditional seeding (checking if data exists before inserting) avoids duplication.
   - Nested loops for generating showtimes allow scalable creation of multiple shows per movie and screen.
   - SQLite is chosen for simplicity, lightweight usage, and ease of integration for small-scale applications.
"""
class DB:
    
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row

    def exec(self, sql: str, params=()):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            self.conn.commit()
            return cur
        except Exception as e:
            print("DB EXEC ERROR:", e)
            raise

    def query(self, sql: str, params=()):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
        except Exception as e:
            print("DB QUERY ERROR:", e)
            raise

    def close(self):
        self.conn.close()


def init_db(db: DB):
    # ── USERS ───────────────────────────────────────────
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

    # ── MOVIES────────────────────────────────────────────
    db.exec("""
    CREATE TABLE IF NOT EXISTS movies (
        movie_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        title        TEXT NOT NULL,
        genre        TEXT,
        language     TEXT,
        duration_min INTEGER,
        synopsis     TEXT,
        poster_path  TEXT
    )
    """)

    # ── THEATRES ─────────────────────────────────────────
    db.exec("""
    CREATE TABLE IF NOT EXISTS theatres (
        theatre_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        city       TEXT,
        address    TEXT
    )
    """)

    # ── SCREENS ──────────────────────────────────────────
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

    # ── SHOWS ────────────────────────────────────────────
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

    # ── BOOKINGS ─────────────────────────────────────────
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

    # ── BOOKING SEATS ────────────────────────────────────
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

    # ── CART ─────────────────────────────────────────────
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

    # ── INDEXES (performance boost) ──────────────────────
    db.exec("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    db.exec("CREATE INDEX IF NOT EXISTS idx_shows_movie ON shows(movie_id)")
    db.exec("CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id)")

    # Seed data
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
             "the crew must confront impossible choices and the true cost of survival.",
             "assets/movieposters/Interstellar.png"),

            ("Arrival",               "Sci-Fi",       "English",  116,
             "When mysterious spacecraft appear around the world, a linguist is "
             "recruited to communicate with the unknown visitors. As she works to "
             "understand their language, the line between past, present, and future "
             "begins to blur.",
             "assets/movieposters/Arrival.png"),

            ("Hacksaw Ridge",         "War/Drama",    "English",  139,
             "Desmond Doss, a deeply religious young man, enlists in the U.S. Army "
             "during World War II but refuses to carry a weapon. His beliefs are put "
             "to the ultimate test when he is sent into one of the war's deadliest battles.",
             "assets/movieposters/HacksawRidge.png"),

            ("Across the Spiderverse","Animation",    "English",  140,
             "Miles Morales reunites with Gwen Stacy and is pulled into a vast "
             "multiverse of Spider-People. When he encounters a powerful new threat, "
             "Miles must redefine what it means to be a hero.",
             "assets/movieposters/AccrossTheSpiderverse.png"),

            ("The Maze Runner",       "Action",       "English",  113,
             "A teenage boy wakes up in a mysterious glade surrounded by a massive "
             "ever-changing maze with no memory of his past. He becomes determined "
             "to uncover the maze's secrets and find a way out.",
             "assets/movieposters/TheMazeRunner.png"),

            ("Howl's Moving Castle",  "Animation",    "Japanese", 119,
             "A young woman named Sophie is transformed into an old woman and seeks "
             "refuge in the magical moving castle of the wizard Howl. As she navigates "
             "a world of war and enchantment, she discovers that nothing is quite "
             "what it seems.",
             "assets/movieposters/HowlsMovingCastle.png"),
        ]

        for m in movies:
            db.exec(
                "INSERT INTO movies(title,genre,language,duration_min,synopsis,poster_path)"
                " VALUES(?,?,?,?,?,?)",
                m
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

        base_times = [
            datetime.now() + timedelta(hours=2),
            datetime.now() + timedelta(hours=5),
        ]

        for movie in movies:
            for screen in screens:
                for showtime in base_times:
                    db.exec(
                        "INSERT INTO shows(movie_id,screen_id,"
                        "show_datetime,base_price) VALUES(?,?,?,?)",
                        (movie["movie_id"], screen["screen_id"],
                         showtime.strftime("%Y-%m-%d %H:%M:%S"), 12.0)
                    )
                    