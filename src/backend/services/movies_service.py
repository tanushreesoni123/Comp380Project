from src.backend.database import DB

"""
a) Module/Class Name:
   MovieService (Movie and Showtime Service Layer)

b) Date: April 8, 2026

c) Programmer: Shivranjini Pandey and Tanushree Soni

d) Description:
   This module handles all movie-related operations including retrieving movie data,
   searching movies, and fetching showtime details. It interacts with the database
   through the DB class and provides clean data access methods for the frontend.

e) Important Functions:

   1. get_all_movies()
      - Input: None
      - Output: List of sqlite3.Row objects (all movies)
      - Description:
        Retrieves all movies from the database, sorted alphabetically by title.

   2. search_movies(keyword: str)
      - Input:
        • keyword (str): Search term entered by user
      - Output:
        • List of sqlite3.Row objects (matching movies)
      - Description:
        Searches for movies where the keyword matches title, genre, or language
        using SQL LIKE pattern matching.

   3. get_movie_by_id(movie_id: int)
      - Input:
        • movie_id (int): Unique ID of the movie
      - Output:
        • sqlite3.Row object (single movie) or None if not found
      - Description:
        Fetches a specific movie from the database using its ID.

   4. get_shows_for_movie(movie_id: int)
      - Input:
        • movie_id (int): Unique ID of the movie
      - Output:
        • List of sqlite3.Row objects (showtime details)
      - Description:
        Retrieves all showtimes for a given movie by joining shows, screens,
        and theatres tables to provide detailed information like time, price,
        and location.

f) Important Data Structures:
   - Uses sqlite3.Row objects to represent movie and show data.
   - SQL JOIN operations combine multiple tables (shows, screens, theatres)
     into a single structured result set.

g) Algorithm/Design Choices:
   - SQL queries with ORDER BY are used for efficient sorting at the database level.
   - LIKE operator is used for simple keyword-based searching due to its simplicity
     and suitability for small-scale applications.
   - JOIN operations are used to efficiently retrieve related data across multiple
     tables instead of multiple separate queries, improving performance.
"""
class MovieService:
    def __init__(self, db: DB):
        self.db = db

    def get_all_movies(self):
        return self.db.query(
            "SELECT * FROM movies ORDER BY title"
        )

    def search_movies(self, keyword: str):
        kw = f"%{keyword.strip()}%"
        return self.db.query(
            """SELECT * FROM movies 
               WHERE title LIKE ? 
               OR genre LIKE ? 
               OR language LIKE ? 
               ORDER BY title""",
            (kw, kw, kw)
        )

    def get_movie_by_id(self, movie_id: int):
        rows = self.db.query(
            "SELECT * FROM movies WHERE movie_id=?",
            (movie_id,)
        )
        return rows[0] if rows else None

    def get_shows_for_movie(self, movie_id: int):
        return self.db.query(
            """SELECT 
                sh.show_id,
                sh.show_datetime,
                sh.base_price,
                sc.name   AS screen_name,
                sc.rows,
                sc.cols,
                th.name   AS theatre_name,
                th.city
               FROM shows sh
               JOIN screens sc ON sh.screen_id = sc.screen_id
               JOIN theatres th ON sc.theatre_id = th.theatre_id
               WHERE sh.movie_id = ?
               ORDER BY sh.show_datetime""",
            (movie_id,)
        )