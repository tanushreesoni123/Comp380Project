import tkinter as tk
<<<<<<< HEAD
from tkinter import messagebox

from src.backend.services.booking_service import BookingService


class SeatPickerPopup(tk.Toplevel):
    def __init__(self, parent, db, user, movie, show):
        super().__init__(parent, bg="gray12")

        self.db = db
        self.user = user
        self.movie = movie
        self.show = show
        self.booking_service = BookingService(db)
        self.selected_seats = set()

        self.title(f"{movie['title']} - Select Seats")
        self.geometry("700x650")
        self.configure(bg="gray12")
        self.resizable(False, False)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"+{x}+{y}")

        self.main_frame = tk.Frame(self, bg="gray12")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_ui()

    def _build_ui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = tk.Label(
            self.main_frame,
            text=f"{self.movie['title']} - Seat Selection",
            bg="gray12",
            fg="sienna1",
            font=("Helvetica", 16, "bold")
        )
        title.pack(pady=(5, 10))

        info = tk.Label(
            self.main_frame,
            text=(
                f"{self.show['theatre_name']} | {self.show['screen_name']}\n"
                f"Price per seat: ${float(self.show['base_price']):.2f}"
            ),
            bg="gray12",
            fg="white",
            font=("Helvetica", 11)
        )
        info.pack(pady=(0, 15))

        legend = tk.Frame(self.main_frame, bg="gray12")
        legend.pack(pady=(0, 15))

        self._legend_box(legend, "gray17", "Available", 0)
        self._legend_box(legend, "sienna1", "Selected", 1)
        self._legend_box(legend, "firebrick3", "Booked", 2)

        screen_label = tk.Label(
            self.main_frame,
            text="SCREEN",
            bg="white",
            fg="black",
            font=("Helvetica", 12, "bold"),
            width=40
        )
        screen_label.pack(pady=(0, 20))

        seats_frame = tk.Frame(self.main_frame, bg="gray12")
        seats_frame.pack()

        taken_seats = set(self.booking_service.get_taken_seats(self.show["show_id"]))

        for r in range(self.show["rows"]):
            row_letter = chr(ord("A") + r)

            row_label = tk.Label(
                seats_frame,
                text=row_letter,
                bg="gray12",
                fg="white",
                font=("Helvetica", 10, "bold"),
                width=3
            )
            row_label.grid(row=r, column=0, padx=(0, 10), pady=5)

            for c in range(1, self.show["cols"] + 1):
                seat_label = f"{row_letter}{c}"

                if seat_label in taken_seats:
                    bg = "firebrick3"
                    state = "disabled"
                    command = None
                    fg = "white"
                elif seat_label in self.selected_seats:
                    bg = "sienna1"
                    state = "normal"
                    command = lambda s=seat_label: self._toggle_seat(s)
                    fg = "gray12"
                else:
                    bg = "gray17"
                    state = "normal"
                    command = lambda s=seat_label: self._toggle_seat(s)
                    fg = "white"

                btn = tk.Button(
                    seats_frame,
                    text=seat_label,
                    width=5,
                    bg=bg,
                    fg=fg,
                    state=state,
                    command=command
                )
                btn.grid(row=r, column=c, padx=4, pady=4)

        selected_text = ", ".join(sorted(self.selected_seats)) if self.selected_seats else "None"
        total = len(self.selected_seats) * float(self.show["base_price"])

        summary = tk.Label(
            self.main_frame,
            text=f"Selected Seats: {selected_text}\nTotal: ${total:.2f}",
            bg="gray12",
            fg="white",
            font=("Helvetica", 11, "bold")
        )
        summary.pack(pady=20)

        button_row = tk.Frame(self.main_frame, bg="gray12")
        button_row.pack(pady=10)

        confirm_btn = tk.Button(
            button_row,
            text="Confirm Booking",
            bg="sienna1",
            fg="gray12",
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=8,
            command=self._confirm_booking
        )
        confirm_btn.pack(side="left", padx=8)

        close_btn = tk.Button(
            button_row,
            text="Close",
            bg="gray17",
            fg="white",
            font=("Helvetica", 11),
            padx=20,
            pady=8,
            command=self.destroy
        )
        close_btn.pack(side="left", padx=8)

    def _legend_box(self, parent, color, text, column):
        wrapper = tk.Frame(parent, bg="gray12")
        wrapper.grid(row=0, column=column, padx=12)

        box = tk.Label(wrapper, bg=color, width=3, height=1)
        box.pack(side="left", padx=(0, 6))

        label = tk.Label(wrapper, text=text, bg="gray12", fg="white")
        label.pack(side="left")

    def _toggle_seat(self, seat_label):
        if seat_label in self.selected_seats:
            self.selected_seats.remove(seat_label)
        else:
            self.selected_seats.add(seat_label)
        self._build_ui()

    def _confirm_booking(self):
        if not self.selected_seats:
            messagebox.showwarning("No Seats", "Please select at least one seat.")
            return

        try:
            result = self.booking_service.create_booking(
                user_id=self.user["user_id"],
                show_id=self.show["show_id"],
                seat_labels=sorted(self.selected_seats)
            )

            seats = ", ".join(result["seat_labels"])
            messagebox.showinfo(
                "Booking Confirmed",
                f"Booking ID: {result['booking_id']}\n"
                f"Seats: {seats}\n"
                f"Total Paid: ${result['total_amount']:.2f}"
            )
            self.destroy()

        except Exception as e:
            messagebox.showerror("Booking Error", str(e))
=======
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
    def __init__(self, master):
        super().__init__(master, bg = "gray12")
        self.master = master
        self.seats = {}
        self.selected_seat_list = []

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
        print("Done")

    def return_to_showtime(self):
        print("Back")
if __name__ == "__main__":
    root = tk.Tk()
    root.title("SeatPickWindow")
    app = SeatPicker(root)
    root.mainloop()







>>>>>>> 2cccef9 (added seat picker UI)
