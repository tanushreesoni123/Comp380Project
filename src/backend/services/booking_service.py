"""
Module: booking_service.py
Author: Tanushree Soni and Shivranjini Pandey
Date: April 30, 2026

Description:
Handles backend booking logic including:
- fetching show details
- checking seat availability
- generating seat layouts
- creating bookings
- retrieving booking details
- canceling bookings
- sending email confirmation
"""

import os
from dotenv import load_dotenv

from src.backend.database import DB
from src.utils import now_iso
from src.backend.services.email_service import EmailService

# Load environment variables
load_dotenv()


class BookingService:
    def __init__(self, db: DB):
        self.db = db

    # ───────────────────────── SHOW DETAILS ─────────────────────────

    def get_show_details(self, show_id: int):
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

    # ───────────────────────── USER DETAILS ─────────────────────────

    def get_user_details(self, user_id: int):
        rows = self.db.query(
            "SELECT name, email FROM users WHERE user_id = ?",
            (user_id,)
        )
        return rows[0] if rows else None

    # ───────────────────────── SEAT LOGIC ─────────────────────────

    def get_taken_seats(self, show_id: int):
        rows = self.db.query(
            """
            SELECT bs.seat_label
            FROM booking_seats bs
            JOIN bookings b ON bs.booking_id = b.booking_id
            WHERE b.show_id = ?
              AND b.status = 'CONFIRMED'
            """,
            (show_id,)
        )
        return [row["seat_label"] for row in rows]

    def get_all_seats_for_show(self, show_id: int):
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
        all_seats = self.get_all_seats_for_show(show_id)
        taken = set(self.get_taken_seats(show_id))
        return [seat for seat in all_seats if seat not in taken]

    # ───────────────────────── CREATE BOOKING ─────────────────────────

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

            # ───────── EMAIL INTEGRATION ─────────

            try:
                user = self.get_user_details(user_id)
                details = self.get_booking_details(booking_id)

                if user and details:
                    email_service = EmailService(
                        smtp_server="smtp.gmail.com",
                        smtp_port=587,
                        sender_email=os.getenv("EMAIL_USER"),
                        sender_password=os.getenv("EMAIL_PASS"),
                    )

                    success, msg = email_service.send_booking_confirmation(
                        to_email=user["email"],
                        customer_name=user["name"],
                        movie_title=details["movie_title"],
                        theatre_name=details["theatre_name"],
                        screen_name=details["screen_name"],
                        show_datetime=details["show_datetime"],
                        seat_labels=details["seats"],
                        total_amount=details["total_amount"],
                        booking_id=booking_id,
                        transaction_ref=None,
                    )

                    if not success:
                        print("\n--- EMAIL SIMULATION ---")
                        print(f"To: {user['email']}")
                        print(f"Booking ID: {booking_id}")
                        print(f"Movie: {details['movie_title']}")
                        print(f"Seats: {', '.join(details['seats'])}")
                        print(f"Total: ${details['total_amount']}")
                        print("--- END EMAIL ---\n")

            except Exception as e:
                print("Email error:", e)

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
        rows = self.db.query(
            """
            SELECT b.booking_id,
                   b.total_amount,
                   b.booking_time,
                   b.status,
                   m.title AS movie_title,
                   sh.show_datetime,
                   th.name AS theatre_name,
                   th.city,
                   sc.name AS screen_name
            FROM bookings b
            JOIN shows sh ON b.show_id = sh.show_id
            JOIN movies m ON sh.movie_id = m.movie_id
            JOIN screens sc ON sh.screen_id = sc.screen_id
            JOIN theatres th ON sc.theatre_id = th.theatre_id
            WHERE b.booking_id = ?
            """,
            (booking_id,)
        )

        if not rows:
            return None

        booking = rows[0]

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
            "theatre_name": booking["theatre_name"],
            "city": booking["city"],
            "screen_name": booking["screen_name"],
            "seats": seats,
            "total_amount": booking["total_amount"],
            "status": booking["status"],
        }

    # ───────────────────────── USER BOOKINGS ─────────────────────────

    def get_user_bookings(self, user_id: int):
        return self.db.query(
            """
            SELECT b.booking_id,
                   b.total_amount,
                   b.booking_time,
                   b.status,
                   m.title AS movie_title,
                   sh.show_datetime,
                   th.name AS theatre_name,
                   th.city,
                   sc.name AS screen_name
            FROM bookings b
            JOIN shows sh ON b.show_id = sh.show_id
            JOIN movies m ON sh.movie_id = m.movie_id
            JOIN screens sc ON sh.screen_id = sc.screen_id
            JOIN theatres th ON sc.theatre_id = th.theatre_id
            WHERE b.user_id = ?
            ORDER BY b.booking_time DESC
            """,
            (user_id,)
        )

    # ───────────────────────── CANCEL BOOKING ─────────────────────────

    def cancel_booking(self, booking_id: int):
        self.db.exec(
            """
            UPDATE bookings
            SET status = 'CANCELED',
                cancel_time = ?
            WHERE booking_id = ?
            """,
            (now_iso(), booking_id)
        )