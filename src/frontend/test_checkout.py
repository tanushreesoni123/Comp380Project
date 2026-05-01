import unittest

def calculate_checkout(selected_seat_list, base_price):
    if selected_seat_list:
        text = ", ".join(selected_seat_list)
    else:
        text = "None"

    total = len(selected_seat_list) * base_price
    return text, total

class TestCheckout(unittest.TestCase):
    
    def test_no_seats_selected(self):
        text, total = calculate_checkout([], 10)

        self.assertEqual(text, "None")
        self.assertEqual(total, 0)

    def test_one_seat(self):
        text, total = calculate_checkout(["A1"], 10)

        self.assertEqual(text, "A1")
        self.assertEqual(total, 10)

    def test_multiple_seats(self):
        text, total = calculate_checkout(["A1", "A2"], 10)

        self.assertEqual(text, "A1, A2")
        self.assertEqual(total, 20)

if __name__ == "__main__":
    unittest.main()
