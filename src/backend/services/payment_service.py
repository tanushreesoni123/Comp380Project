import uuid

from src.backend.database import DB
from src.backend.services.booking_service import BookingService
from src.utils import now_iso


class PaymentService:
    def __init__(self, db: DB):
        self.db = db
        self.booking_service = BookingService(db)

    # ───────────────────────── MAIN PAYMENT FUNCTION ─────────────────────────

    def make_payment(
        self,
        booking_id: int,
        payment_method: str,
        card_number: str | None = None,
        card_holder: str | None = None,
        expiry_month: int | None = None,
        expiry_year: int | None = None,
        cvv: str | None = None,
    ):
        booking = self.booking_service.get_booking_details(booking_id)

        if not booking:
            return False, "Booking not found.", None

        if booking["status"] != "CONFIRMED":
            return False, "Invalid booking status.", None

        method = (payment_method or "").strip().upper()

        if method not in {"CARD", "CASH", "UPI"}:
            return False, "Unsupported payment method.", None

        # Validate card if needed
        if method == "CARD":
            ok, message, card_last4 = self._validate_card(
                card_number,
                card_holder,
                expiry_month,
                expiry_year,
                cvv,
            )
            if not ok:
                return False, message, None
        else:
            card_last4 = None

        transaction_ref = self._generate_transaction_ref()

        try:
            self.db.exec(
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
                    booking["total_amount"],
                    method,
                    card_last4,
                    transaction_ref,
                    now_iso(),
                ),
            )

            return True, "Payment successful.", {
                "booking_id": booking_id,
                "transaction_ref": transaction_ref,
                "amount": booking["total_amount"],
                "payment_method": method,
            }

        except Exception as e:
            return False, f"Payment failed: {e}", None

    # ───────────────────────── GET PAYMENT ─────────────────────────

    def get_payment_by_booking(self, booking_id: int):
        rows = self.db.query(
            """
            SELECT payment_id, booking_id, amount, payment_method,
                   card_last4, transaction_ref, status, paid_at
            FROM payments
            WHERE booking_id = ?
            """,
            (booking_id,),
        )
        return rows[0] if rows else None

    # ───────────────────────── HELPERS ─────────────────────────

    def _validate_card(
        self,
        card_number,
        card_holder,
        expiry_month,
        expiry_year,
        cvv,
    ):
        digits = "".join(ch for ch in (card_number or "") if ch.isdigit())

        if len(digits) != 16:
            return False, "Card number must contain 16 digits.", None

        if not (card_holder or "").strip():
            return False, "Card holder name is required.", None

        if expiry_month is None or expiry_year is None:
            return False, "Expiry date required.", None

        if not (1 <= int(expiry_month) <= 12):
            return False, "Invalid expiry month.", None

        if int(expiry_year) < 2025:
            return False, "Invalid expiry year.", None

        cvv_digits = "".join(ch for ch in (cvv or "") if ch.isdigit())
        if len(cvv_digits) not in {3, 4}:
            return False, "Invalid CVV.", None

        return True, "OK", digits[-4:]

    def _generate_transaction_ref(self):
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"