import uuid
from typing import Iterable

from src.backend.database import DB
from src.utils import now_iso


class PaymentService:
    """
    Backend-only payment service for local/demo use.
    It validates payment input, checks seat availability,
    creates a confirmed booking, and stores payment info.
    """

    def __init__(self, db: DB):
        self.db = db

    def make_payment(
        self,
        user_id: int,
        show_id: int,
        seat_labels: Iterable[str],
        payment_method: str,
        card_number: str | None = None,
        card_holder: str | None = None,
        expiry_month: int | None = None,
        expiry_year: int | None = None,
        cvv: str | None = None,
    ) -> tuple[bool, str, dict | None]:
        cleaned_seats = self._normalize_seats(seat_labels)
        if not cleaned_seats:
            return False, "Please select at least one seat.", None

        show_row = self._get_show(show_id)
        if not show_row:
            return False, "Show not found.", None

        method = (payment_method or "").strip().upper()
        if method not in {"CARD", "CASH", "UPI"}:
            return False, "Unsupported payment method.", None

        if method == "CARD":
            ok, message, card_last4 = self._validate_card(
                card_number=card_number,
                card_holder=card_holder,
                expiry_month=expiry_month,
                expiry_year=expiry_year,
                cvv=cvv,
            )
            if not ok:
                return False, message, None
        else:
            card_last4 = None

        unavailable = self._find_unavailable_seats(show_id, cleaned_seats)
        if unavailable:
            return False, f"These seats are already booked: {', '.join(unavailable)}", None

        base_price = float(show_row["base_price"])
        total_amount = round(base_price * len(cleaned_seats), 2)
        booking_time = now_iso()
        transaction_ref = self._generate_transaction_ref()

        cur = self.db.conn.cursor()
        try:
            cur.execute("BEGIN")

            cur.execute(
                """
                INSERT INTO bookings(user_id, show_id, booking_time, total_amount, status)
                VALUES (?, ?, ?, ?, 'CONFIRMED')
                """,
                (user_id, show_id, booking_time, total_amount),
            )
            booking_id = cur.lastrowid

            for seat in cleaned_seats:
                cur.execute(
                    """
                    INSERT INTO booking_seats(booking_id, seat_label, seat_price)
                    VALUES (?, ?, ?)
                    """,
                    (booking_id, seat, base_price),
                )

            cur.execute(
                """
                INSERT INTO payments(
                    booking_id,
                    amount,
                    payment_method,
                    card_last4,
                    transaction_ref,
                    status,
                    paid_at
                )
                VALUES (?, ?, ?, ?, ?, 'SUCCESS', ?)
                """,
                (
                    booking_id,
                    total_amount,
                    method,
                    card_last4,
                    transaction_ref,
                    booking_time,
                ),
            )

            cur.execute(
                "DELETE FROM cart WHERE user_id=? AND show_id=? AND seat_label IN (%s)"
                % ",".join(["?"] * len(cleaned_seats)),
                (user_id, show_id, *cleaned_seats),
            )

            self.db.conn.commit()
        except Exception as exc:
            self.db.conn.rollback()
            return False, f"Payment failed: {exc}", None

        return True, "Payment successful.", {
            "booking_id": booking_id,
            "transaction_ref": transaction_ref,
            "amount": total_amount,
            "payment_method": method,
            "seats": cleaned_seats,
            "show_id": show_id,
        }

    def get_payment_by_booking(self, booking_id: int):
        rows = self.db.query(
            """
            SELECT payment_id, booking_id, amount, payment_method, card_last4,
                   transaction_ref, status, paid_at
            FROM payments
            WHERE booking_id=?
            """,
            (booking_id,),
        )
        return rows[0] if rows else None

    def _get_show(self, show_id: int):
        rows = self.db.query(
            "SELECT show_id, base_price FROM shows WHERE show_id=?",
            (show_id,),
        )
        return rows[0] if rows else None

    def _find_unavailable_seats(self, show_id: int, seat_labels: list[str]) -> list[str]:
        placeholders = ",".join(["?"] * len(seat_labels))
        rows = self.db.query(
            f"""
            SELECT bs.seat_label
            FROM booking_seats bs
            JOIN bookings b ON b.booking_id = bs.booking_id
            WHERE b.show_id = ?
              AND b.status = 'CONFIRMED'
              AND bs.seat_label IN ({placeholders})
            """,
            (show_id, *seat_labels),
        )
        return [row["seat_label"] for row in rows]

    def _normalize_seats(self, seat_labels: Iterable[str]) -> list[str]:
        cleaned = []
        seen = set()
        for seat in seat_labels or []:
            value = str(seat).strip().upper()
            if value and value not in seen:
                cleaned.append(value)
                seen.add(value)
        return cleaned

    def _validate_card(
        self,
        card_number: str | None,
        card_holder: str | None,
        expiry_month: int | None,
        expiry_year: int | None,
        cvv: str | None,
    ) -> tuple[bool, str, str | None]:
        digits = "".join(ch for ch in (card_number or "") if ch.isdigit())
        if len(digits) != 16:
            return False, "Card number must contain 16 digits.", None

        if not (card_holder or "").strip():
            return False, "Card holder name is required.", None

        if expiry_month is None or expiry_year is None:
            return False, "Card expiry month and year are required.", None

        if not (1 <= int(expiry_month) <= 12):
            return False, "Expiry month must be between 1 and 12.", None

        if int(expiry_year) < 2025:
            return False, "Card expiry year is invalid.", None

        cvv_digits = "".join(ch for ch in (cvv or "") if ch.isdigit())
        if len(cvv_digits) not in {3, 4}:
            return False, "CVV must be 3 or 4 digits.", None

        return True, "OK", digits[-4:]

    def _generate_transaction_ref(self) -> str:
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"