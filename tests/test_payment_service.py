import pytest
from src.backend.database import DB, init_db
from src.backend.services.booking_service import BookingService
from src.backend.services.payment_service import PaymentService


@pytest.fixture
def setup_services():
    db = DB(":memory:")
    init_db(db)

    booking_service = BookingService(db)
    payment_service = PaymentService(db)

    return booking_service, payment_service


# ───────────────────────── SUCCESS CASE ─────────────────────────

def test_payment_success(setup_services):
    booking_service, payment_service = setup_services

    booking = booking_service.create_booking(
        user_id=1,
        show_id=1,
        seat_labels=["A1"]
    )

    success, msg, data = payment_service.make_payment(
        booking_id=booking["booking_id"],
        payment_method="CASH"
    )

    assert success is True
    assert data["amount"] > 0
    assert data["booking_id"] == booking["booking_id"]


# ───────────────────────── INVALID PAYMENT METHOD ─────────────────────────

def test_invalid_payment_method(setup_services):
    booking_service, payment_service = setup_services

    booking = booking_service.create_booking(1, 1, ["A2"])

    success, msg, data = payment_service.make_payment(
        booking_id=booking["booking_id"],
        payment_method="BITCOIN"
    )

    assert success is False
    assert "Unsupported" in msg


# ───────────────────────── INVALID CARD DETAILS ─────────────────────────

def test_invalid_card_details(setup_services):
    booking_service, payment_service = setup_services

    booking = booking_service.create_booking(1, 1, ["A3"])

    success, msg, data = payment_service.make_payment(
        booking_id=booking["booking_id"],
        payment_method="CARD",
        card_number="123",   # invalid
        card_holder="Test",
        expiry_month=12,
        expiry_year=2026,
        cvv="123"
    )

    assert success is False
    assert "Card number" in msg


# ───────────────────────── DUPLICATE PAYMENT ─────────────────────────

def test_duplicate_payment(setup_services):
    booking_service, payment_service = setup_services

    booking = booking_service.create_booking(1, 1, ["A4"])

    payment_service.make_payment(
        booking_id=booking["booking_id"],
        payment_method="CASH"
    )

    success, msg, data = payment_service.make_payment(
        booking_id=booking["booking_id"],
        payment_method="CASH"
    )

    assert success is False


# ───────────────────────── GET PAYMENT ─────────────────────────

def test_get_payment(setup_services):
    booking_service, payment_service = setup_services

    booking = booking_service.create_booking(1, 1, ["A5"])

    payment_service.make_payment(
        booking_id=booking["booking_id"],
        payment_method="CASH"
    )

    payment = payment_service.get_payment_by_booking(
        booking["booking_id"]
    )

    assert payment is not None
    assert payment["booking_id"] == booking["booking_id"]