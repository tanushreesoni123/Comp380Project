import tkinter as tk
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