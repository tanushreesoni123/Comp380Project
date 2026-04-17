from src.backend.database import DB
from src.utils import now_iso


class BookingService:
    def __init__(self, db: DB):
        self.db = db

    def get_show_details(self, show_id: int):
        rows = self.db.query(
            """
            SELECT
                sh.show_id,
                sh.movie_id,
                sh.show_datetime,
                sh.base_price,
                sc.screen_id,
                sc.name AS screen_name,
                sc.rows,
                sc.cols,
                th.name AS theatre_name,
                th.city
            FROM shows sh
            JOIN screens sc ON sh.screen_id = sc.screen_id
            JOIN theatres th ON sc.theatre_id = th.theatre_id
            WHERE sh.show_id = ?
            """,
            (show_id,)
        )
        return rows[0] if rows else None

    def get_taken_seats(self, show_id: int):
        rows = self.db.query(
            """
            SELECT bs.seat_label
            FROM booking_seats bs
            JOIN bookings b ON bs.booking_id = b.booking_id
            WHERE b.show_id = ?
              AND b.status = 'CONFIRMED'
            ORDER BY bs.seat_label
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