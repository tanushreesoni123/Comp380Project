import tkinter as tk
from tkinter import ttk, messagebox

#from src.backend.database import DB

class MovieSeat:

    def __init__(self, seat_id, row, num, availability = "available"):
        self.seat_id = seat_id
        self.row = row
        self.num = num
        self.availability = availability
        self.button = "None"


class SeatPicker(tk.Frame):
    def __init__(self, master, movie, showtime, base_price, show_id=1): ##added movie, showtime, base_price, show_id
        super().__init__(master, bg = "gray12")
        self.master = master
        self.seats = {}
        self.selected_seat_list = []
        self.movie = movie
        self.showtime = showtime #just added
        self.base_price = base_price #just added
        self.show_id = show_id  # Store show_id

        window_width = 1000
        window_height = 800

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.pack(fill = "both", expand = True)


        self.seat_layout = {
            "A": 11,
            "B": 13,
            "C": 15,
            "D": 15,
            "E": 15,
            "F": 15,
            "G": 15,

        }

        self.max_columns = max(self.seat_layout.values())
        self.build_ui()
        self.create_seat()

    def build_ui(self):
        self.configure(bg = "gray12")

        self.top = tk.Frame(self, bg = "gray10")
        self.top.pack(fill = "x", padx = (20,20))

        self.return_button = tk.Button(self.top, text = "Return", bg = "gray10", fg = "white", relief = "flat",
                            font =("Helvetica", 8, "bold"), height = 2, width = 5, command = self.return_to_showtime)

        self.return_button.pack(side = "left", padx = 10, pady=10)

        self.screen_title = tk.Label(self.top, text = "SCREEN", bg = "gray10", fg = "white", 
                            font =("Helvetica", 30, "bold"))
        self.screen_title.pack(side = "top", anchor = "n", padx = 10, pady = 20)


        self.seats_container = tk.Frame(self, bg = "gray10")
        self.seats_container.pack(expand = True, fill = "both", padx = 40, pady = 20)
        self.seats_center = tk.Frame(self.seats_container, bg = "gray10")
        self.seats_center.pack(expand = True)

        self.bottom = tk.Frame(self, bg = "gray10")
        self.bottom.pack(expand = True, fill = "both", padx = 40, pady = 20)

        self.checkout_list = tk.Label(self.bottom, text = "Selected Seats: None", bg = "gray10", fg = "white", 
                            font =("Helvetica", 15, "bold"), wraplength = 600)
        self.checkout_list.pack(side = "left", padx = (20,20))


        self.next_button = tk.Button(self.bottom, text = "Next", bg = "sienna1", fg = "gray12", 
                      font =("Helvetica", 12, "bold"),
                     highlightbackground = "gray20", height = 2, width = 8, command = self.checkout)

        self.next_button.pack(side = "right", padx = 20, pady=10)


    def clicked_seat(self, seat_id):
        seat = self.seats[seat_id]

        if seat.availability == "available":
            seat.availability = "selected"
            seat.button.config(bg = "sienna1", fg = "gray10")
            self.selected_seat_list.append(seat_id)

        elif seat.availability == "selected":
            seat.availability = "available"
            seat.button.config(bg = "gray20", fg = "white")
            self.selected_seat_list.remove(seat_id)

        self.update_checkout_list()


    def create_seat(self):
        for row_index, (row, seat_total) in enumerate(self.seat_layout.items()):

            center = (self.max_columns - seat_total) // 2
            for seat_num in range(1, seat_total +1):
                seat_id = f"{row}{seat_num}"
                seat = MovieSeat(seat_id, row, seat_num)

                seat_button = tk.Button(self.seats_center, text = seat_id, bg = "gray20",
                        fg = "white", height = 3, width = 6, 
                        command = lambda e = seat_id: self.clicked_seat(e))
                seat_button.grid(row = row_index, column = center + (seat_num -1), padx = 4.2, pady = 3)

                seat.button = seat_button
                self.seats[seat_id] = seat

    def update_checkout_list(self):
        if self.selected_seat_list:
            text = ", ".join(self.selected_seat_list)
        
        else:
            text = "None"

        self.checkout_list.configure(text = f"Selected Seats: {text}")

    def checkout(self):
        if not self.selected_seat_list:
            messagebox.showwarning("No Seats", "Please select at least one seat.")
            return

        # Import inside to avoid circular import
        from src.frontend.customer.payment_window import PaymentWindow

        # Switch to payment screen
        self.master.switch_frame(
            PaymentWindow,
            self.selected_seat_list,
            self.base_price,
            self.show_id
        )

    def return_to_showtime(self):
        """Return to movie selection screen"""
        # Save db and user before destroying
        db = self.master.db
        user = self.master.current_user
        
        # Destroy current seat picker frame
        self.destroy()
        
        # Reset window geometry for movie selection screen
        window_width = 1000
        window_height = 800
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Go back to movie selection (CustomerWindow)
        from src.frontend.customer.customer_window import CustomerWindow
        self.master.switch_frame(CustomerWindow, db, user)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("SeatPickWindow")
    app = SeatPicker(root)
    root.mainloop()


