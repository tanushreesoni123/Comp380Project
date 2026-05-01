"""
Module: cart_service.py
Author: Shivranjini Pandey
Date: April 30, 2026

Description:
Handles cart-related operations for the cinema booking system.
Allows users to add seats to cart, view cart contents, remove seats,
and clear cart before final booking.
"""

from src.backend.database import DB
from src.utils import now_iso


class CartService:
    def __init__(self, db: DB):
        self.db = db

    # ───────────────────────── ADD TO CART ─────────────────────────

    def add_to_cart(self, user_id: int, show_id: int, seat_label: str):
        """Add a seat to the user's cart"""

        seat = seat_label.strip().upper()

        try:
            self.db.exec(
                """
                INSERT INTO cart(user_id, show_id, seat_label, added_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, show_id, seat, now_iso())
            )
            return True, "Seat added to cart."

        except Exception:
            return False, "Seat already in cart."

    # ───────────────────────── GET CART ─────────────────────────

    def get_cart(self, user_id: int):
        """Fetch all cart items for a user"""

        return self.db.query(
            """
            SELECT c.cart_id,
                   c.show_id,
                   c.seat_label,
                   c.added_at,
                   m.title AS movie_title,
                   sh.show_datetime,
                   th.name AS theatre_name,
                   th.city,
                   sc.name AS screen_name
            FROM cart c
            JOIN shows sh ON c.show_id = sh.show_id
            JOIN movies m ON sh.movie_id = m.movie_id
            JOIN screens sc ON sh.screen_id = sc.screen_id
            JOIN theatres th ON sc.theatre_id = th.theatre_id
            WHERE c.user_id = ?
            ORDER BY c.added_at DESC
            """,
            (user_id,)
        )

    # ───────────────────────── REMOVE FROM CART ─────────────────────────

    def remove_from_cart(self, user_id: int, show_id: int, seat_label: str):
        """Remove a specific seat from cart"""

        self.db.exec(
            """
            DELETE FROM cart
            WHERE user_id = ? AND show_id = ? AND seat_label = ?
            """,
            (user_id, show_id, seat_label.strip().upper())
        )

    # ───────────────────────── CLEAR CART ─────────────────────────

    def clear_cart(self, user_id: int, show_id: int):
        """Remove all seats for a show from cart"""

        self.db.exec(
            """
            DELETE FROM cart
            WHERE user_id = ? AND show_id = ?
            """,
            (user_id, show_id)
        )

    # ───────────────────────── CHECK CART SEATS ─────────────────────────

    def get_cart_seats(self, user_id: int, show_id: int):
        """Return list of seat labels currently in cart"""

        rows = self.db.query(
            """
            SELECT seat_label
            FROM cart
            WHERE user_id = ? AND show_id = ?
            """,
            (user_id, show_id)
        )

        return [row["seat_label"] for row in rows]