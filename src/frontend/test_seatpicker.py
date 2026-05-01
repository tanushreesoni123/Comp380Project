import unittest

class MockSeat:
    def __init__(self, seat_id, availability):
        self.seat_id = seat_id
        self.availability = availability

def toggle_seat(seat, selected_list):
    if seat.availability == "taken":
        return
    
    if seat.availability == "available":
        seat.availability = "selected"
        selected_list.append(seat.seat_id)

    elif seat.availability == "selected":
        seat.availability = "available"
        selected_list.remove(seat.seat_id)
       


class TestSeatPicker(unittest.TestCase):

    def test_taken_seat(self):
        seat = MockSeat("A1", "taken")
        selected = []

        toggle_seat(seat, selected)

        self.assertEqual(seat.availability, "taken")
        self.assertEqual(selected, [])
    
    def test_select_available(self):
        seat = MockSeat("A1", "available")
        selected = []

        toggle_seat(seat, selected)

        self.assertEqual(seat.availability, "selected")
        self.assertIn("A1", selected)

    def test_deselect_seat(self):
        seat = MockSeat("A1", "selected")
        selected = ["A1"]

        toggle_seat(seat, selected)

        self.assertEqual(seat.availability, "available")
        self.assertNotIn("A1", selected)

if __name__ == "__main__":
    unittest.main()

