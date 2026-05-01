"""
Module: report_service.py
Author: Shivranjini Pandey
Date: May 1, 2026

Description:
Provides reporting functionality for managers including:
- total revenue
- total bookings
- popular movies
- revenue per movie
- recent booking activity
"""

from src.backend.database import DB


class ReportService:
    def __init__(self, db: DB):
        self.db = db

    # ───────────────────────── TOTAL REVENUE ─────────────────────────

    def get_total_revenue(self):
        rows = self.db.query(
            """
            SELECT SUM(total_amount) AS total_revenue
            FROM bookings
            WHERE status = 'CONFIRMED'
            """
        )
        return rows[0]["total_revenue"] or 0.0

    # ───────────────────────── TOTAL BOOKINGS ─────────────────────────

    def get_total_bookings(self):
        rows = self.db.query(
            """
            SELECT COUNT(*) AS total_bookings
            FROM bookings
            WHERE status = 'CONFIRMED'
            """
        )
        return rows[0]["total_bookings"]

    # ───────────────────────── BOOKINGS PER MOVIE ─────────────────────────

    def get_popular_movies(self):
        return self.db.query(
            """
            SELECT m.title AS movie_title,
                   COUNT(b.booking_id) AS total_bookings
            FROM bookings b
            JOIN shows sh ON b.show_id = sh.show_id
            JOIN movies m ON sh.movie_id = m.movie_id
            WHERE b.status = 'CONFIRMED'
            GROUP BY m.title
            ORDER BY total_bookings DESC
            """
        )

    # ───────────────────────── REVENUE PER MOVIE ─────────────────────────

    def get_revenue_per_movie(self):
        return self.db.query(
            """
            SELECT m.title AS movie_title,
                   SUM(b.total_amount) AS revenue
            FROM bookings b
            JOIN shows sh ON b.show_id = sh.show_id
            JOIN movies m ON sh.movie_id = m.movie_id
            WHERE b.status = 'CONFIRMED'
            GROUP BY m.title
            ORDER BY revenue DESC
            """
        )

    # ───────────────────────── RECENT BOOKINGS ─────────────────────────

    def get_recent_bookings(self, limit: int = 5):
        return self.db.query(
            """
            SELECT b.booking_id,
                   m.title AS movie_title,
                   b.total_amount,
                   b.booking_time
            FROM bookings b
            JOIN shows sh ON b.show_id = sh.show_id
            JOIN movies m ON sh.movie_id = m.movie_id
            WHERE b.status = 'CONFIRMED'
            ORDER BY b.booking_time DESC
            LIMIT ?
            """,
            (limit,)
        )