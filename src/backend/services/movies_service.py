from src.backend.database import DB


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