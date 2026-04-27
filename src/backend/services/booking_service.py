"""
Module: booking_service.py
Author: Tanushree Soni
Date: 2026-04-17

Description:
This module handles backend booking logic for the cinema system.
It retrieves show details, checks seat availability, generates seat layouts,
and creates bookings in the database while preventing duplicate seat reservations.
"""
from src.backend.database import DB
from src.utils import now_iso


class BookingService:
    def __init__(self, db: DB):
        self.db = db

    def get_show_details(self, show_id):
        rows = self.db.query(
    """
    Retrieves details for a specific show.

    Args:
        show_id (int): ID of the show

    Returns:
        dict: Show details including movie, theatre, screen, and pricing
    """
            (show_id,)
        )
        return rows[0] if rows else None

    def get_taken_seats(self, show_id: int):
        rows = self.db.query(
              """
    Retrieves seats that are already booked for a show.

    Args:
        show_id (int): ID of the show

    Returns:
        list: List of booked seat labels (e.g., ['A1', 'B2'])
    """
            (show_id,)
        )
        return [row["seat_label"] for row in rows]

    def get_all_seats_for_show(self, show_id: int):
        show = self.get_show_details(show_id)
        
        if not show:
            return []

        """
    Generates all seat labels for a show based on screen size.

    Args:
        show_id (int): ID of the show

    Returns:
        list: All possible seat labels (e.g., ['A1', 'A2', ...])
    """

        seats = []
        for r in range(show["rows"]):
            row_letter = chr(ord("A") + r)
            for c in range(1, show["cols"] + 1):
                seats.append(f"{row_letter}{c}")
        return seats

    def get_available_seats(self, show_id: int):
        all_seats = self.get_all_seats_for_show(show_id)
        taken = set(self.get_taken_seats(show_id))
        return [seat for seat in all_seats if seat not in taken]
    
    """
    Returns available (unbooked) seats for a show.

    Args:
        show_id (int): ID of the show

    Returns:
        list: Available seat labels
    """

    def create_booking(self, user_id: int, show_id: int, seat_labels: list[str]):
        if not seat_labels:
            raise ValueError("Please select at least one seat.")

        normalized = []
        for seat in seat_labels:
            seat = seat.strip().upper()
            if seat and seat not in normalized:
                normalized.append(seat)

        show = self.get_show_details(show_id)
        if not show:
            raise ValueError("Show not found.")

        valid_seats = set(self.get_all_seats_for_show(show_id))
        invalid = [seat for seat in normalized if seat not in valid_seats]
        if invalid:
            raise ValueError(f"Invalid seat(s): {', '.join(invalid)}")

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

            cur.execute(
                """
                INSERT INTO bookings(user_id, show_id, booking_time, total_amount, status, cancel_time)
                VALUES (?, ?, ?, ?, 'CONFIRMED', NULL)
                """,
                (user_id, show_id, now_iso(), total_amount)
            )
            booking_id = cur.lastrowid

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
        def create_booking(self, user_id, show_id, seat_labels):
    
    
           """
    Creates a new booking for selected seats.

    Args:
        user_id (int): ID of the user
        show_id (int): ID of the show
        seat_labels (list): List of selected seat labels

    Returns:
        dict: Booking confirmation including booking ID and total amount

    Raises:
        ValueError: If seats are invalid or already booked
    """