"""
Module: booking_service.py
Author: Tanushree Soni
Date: 2026-04-17

Description:
Handles backend booking logic including:
- fetching show details
- checking seat availability
- generating seat layouts
- creating bookings
- retrieving booking details
"""

from src.backend.database import DB
from src.utils import now_iso


class BookingService:
    def __init__(self, db: DB):
        self.db = db

    # ───────────────────────── SHOW DETAILS ─────────────────────────

    def get_show_details(self, show_id: int):
        """Fetch show details including seat layout and price"""
        rows = self.db.query(
            """
            SELECT sh.show_id,
                   sh.base_price,
                   sc.rows,
                   sc.cols
            FROM shows sh
            JOIN screens sc ON sh.screen_id = sc.screen_id
            WHERE sh.show_id = ?
            """,
            (show_id,)
        )
        return rows[0] if rows else None

    # ───────────────────────── SEAT LOGIC ─────────────────────────

    def get_taken_seats(self, show_id: int):
        """Return list of already booked seat labels"""
        rows = self.db.query(
            """
            SELECT bs.seat_label
            FROM booking_seats bs
            JOIN bookings b ON bs.booking_id = b.booking_id
            WHERE b.show_id = ?
            """,
            (show_id,)
        )
        return [row["seat_label"] for row in rows]

    def get_all_seats_for_show(self, show_id: int):
        """Generate all possible seat labels (A1, A2, ...)"""
        show = self.get_show_details(show_id)
        if not show:
            return []

        seats = []
        for r in range(show["rows"]):
            row_letter = chr(ord("A") + r)
            for c in range(1, show["cols"] + 1):
                seats.append(f"{row_letter}{c}")
        return seats

    def get_available_seats(self, show_id: int):
        """Return available (unbooked) seats"""
        all_seats = self.get_all_seats_for_show(show_id)
        taken = set(self.get_taken_seats(show_id))
        return [seat for seat in all_seats if seat not in taken]

    # ───────────────────────── CREATE BOOKING ─────────────────────────

    def create_booking(self, user_id: int, show_id: int, seat_labels: list[str]):
        """Create booking after validating seats"""

        if not seat_labels:
            raise ValueError("Please select at least one seat.")

        # Normalize seat labels
        normalized = []
        for seat in seat_labels:
            seat = seat.strip().upper()
            if seat and seat not in normalized:
                normalized.append(seat)

        show = self.get_show_details(show_id)
        if not show:
            raise ValueError("Show not found.")

        # Validate seats
        valid_seats = set(self.get_all_seats_for_show(show_id))
        invalid = [seat for seat in normalized if seat not in valid_seats]
        if invalid:
            raise ValueError(f"Invalid seat(s): {', '.join(invalid)}")

        # Check if seats already booked
        taken = set(self.get_taken_seats(show_id))
        already_taken = [seat for seat in normalized if seat in taken]
        if already_taken:
            raise ValueError(
                f"These seat(s) are already booked: {', '.join(already_taken)}"
            )

        total_amount = len(normalized) * float(show["base_price"])

        cur = self.db.conn.cursor()
        try:
            cur.execute("BEGIN")

            # Insert booking
            cur.execute(
                """
                INSERT INTO bookings(user_id, show_id, booking_time, total_amount, status, cancel_time)
                VALUES (?, ?, ?, ?, 'CONFIRMED', NULL)
                """,
                (user_id, show_id, now_iso(), total_amount)
            )
            booking_id = cur.lastrowid

            # Insert seats
            for seat in normalized:
                cur.execute(
                    """
                    INSERT INTO booking_seats(booking_id, seat_label, seat_price)
                    VALUES (?, ?, ?)
                    """,
                    (booking_id, seat, float(show["base_price"]))
                )

            self.db.conn.commit()

            return {
                "booking_id": booking_id,
                "show_id": show_id,
                "seat_labels": normalized,
                "total_amount": total_amount,
            }

        except Exception:
            self.db.conn.rollback()
            raise

    # ───────────────────────── BOOKING DETAILS ─────────────────────────

    def get_booking_details(self, booking_id: int):
        """Fetch complete booking details for confirmation screen"""

        booking_rows = self.db.query(
            """
            SELECT b.booking_id,
                   b.total_amount,
                   b.booking_time,
                   m.title AS movie_title,
                   sh.show_datetime
            FROM bookings b
            JOIN shows sh ON b.show_id = sh.show_id
            JOIN movies m ON sh.movie_id = m.movie_id
            WHERE b.booking_id = ?
            """,
            (booking_id,)
        )

        if not booking_rows:
            return None

        booking = booking_rows[0]

        seat_rows = self.db.query(
            """
            SELECT seat_label
            FROM booking_seats
            WHERE booking_id = ?
            """,
            (booking_id,)
        )

        seats = [row["seat_label"] for row in seat_rows]

        return {
            "booking_id": booking["booking_id"],
            "movie_title": booking["movie_title"],
            "show_datetime": booking["show_datetime"],
            "seats": seats,
            "total_amount": booking["total_amount"],
        }

    # ───────────────────────── USER BOOKINGS (OPTIONAL) ─────────────────────────

    def get_user_bookings(self, user_id: int):
        """Fetch all bookings for a user"""
        return self.db.query(
            """
            SELECT booking_id, show_id, total_amount, booking_time, status
            FROM bookings
            WHERE user_id = ?
            ORDER BY booking_time DESC
            """,
            (user_id,)
        )
