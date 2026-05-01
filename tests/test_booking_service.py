import pytest
from src.backend.database import DB, init_db
from src.backend.services.booking_service import BookingService


@pytest.fixture
def booking_service():
    db = DB(":memory:") # in memory database
    init_db(db)
    return BookingService(db)


def test_get_show_details(booking_service):
    show = booking_service.get_show_details(1)
    assert show is not None


def test_get_all_seats(booking_service):
    seats = booking_service.get_all_seats_for_show(1)
    assert "A1" in seats


def test_get_available_seats(booking_service):
    seats = booking_service.get_available_seats(1)
    assert len(seats) > 0


def test_create_booking_success(booking_service):
    result = booking_service.create_booking(
        user_id=1,
        show_id=1,
        seat_labels=["A1", "A2"]
    )
    assert result["booking_id"] is not None


def test_duplicate_seat_booking(booking_service):
    booking_service.create_booking(1, 1, ["A3"])

    with pytest.raises(ValueError):
        booking_service.create_booking(1, 1, ["A3"])


def test_invalid_seat(booking_service):
    with pytest.raises(ValueError):
        booking_service.create_booking(1, 1, ["Z99"])


def test_cancel_booking(booking_service):
    result = booking_service.create_booking(1, 1, ["B1"])
    booking_service.cancel_booking(result["booking_id"])

    details = booking_service.get_booking_details(result["booking_id"])
    assert details["status"] == "CANCELED"


def test_get_booking_details(booking_service):
    result = booking_service.create_booking(1, 1, ["C1"])
    details = booking_service.get_booking_details(result["booking_id"])

    assert details is not None
    assert len(details["seats"]) == 1