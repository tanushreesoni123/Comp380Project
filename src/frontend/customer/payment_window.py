import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from src.backend.services.booking_service import BookingService
from src.backend.services.payment_service import PaymentService
from src.backend.database import DB


class PaymentWindow(tk.Frame):
    def __init__(self, master, selected_seats, base_price, show_id=1):
        super().__init__(master, bg="gray12")

        self.selected_seats = selected_seats
        self.base_price = base_price
        self.show_id = show_id  # Store the show_id

        self.pack(fill="both", expand=True)

        self._build_ui()

        self.db = self.master.db if hasattr(self.master, "db") else DB("movies.db")
        self.booking_service = BookingService(self.db)
        self.payment_service = PaymentService(self.db)

    def _build_ui(self):
        container = tk.Frame(self, bg="gray12", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Payment",
                 bg="gray12", fg="sienna1",
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        tk.Label(container, text="Selected Seats:",
                 bg="gray12", fg="white").pack()

        tk.Label(container,
                 text=", ".join(self.selected_seats),
                 bg="gray17", fg="sienna1",
                 padx=10, pady=10).pack(fill="x", pady=10)
        total = self.base_price * len(self.selected_seats)

        tk.Label(container,
                 text=f"Total: ${total:.2f}",
                 bg="gray12", fg="sienna1",
                 font=("Helvetica", 14, "bold")).pack(pady=10)

        button_frame = tk.Frame(container, bg="gray12")
        button_frame.pack(pady=20)

        tk.Button(button_frame,
                  text="Pay Now",
                  bg="sienna1", fg="gray12",
                  command=self._on_pay).pack(side="left", padx=5)

        tk.Button(button_frame,
                  text="Back to Movies",
                  bg="gray17", fg="white",
                  command=self._back_to_movies).pack(side="left", padx=5)

        form = tk.Frame(container, bg="gray17", padx=10, pady=10)
        form.pack(fill="x", pady=10)

        # Name on Card
        tk.Label(form, text="Name on Card:", bg="gray17", fg="white")\
            .grid(row=0, column=0, sticky="w", pady=5)
        self.card_name = tk.Entry(form, bg="gray11", fg="white", insertbackground="white")
        self.card_name.grid(row=0, column=1, pady=5)

        # Card Number
        tk.Label(form, text="Card Number:", bg="gray17", fg="white")\
            .grid(row=1, column=0, sticky="w", pady=5)
        self.card_number = tk.Entry(form, bg="gray11", fg="white", insertbackground="white")
        self.card_number.grid(row=1, column=1, pady=5)

        # Expiration Date (MM/YY)
        tk.Label(form, text="Expiry (MM/YY):", bg="gray17", fg="white")\
            .grid(row=2, column=0, sticky="w", pady=5)
        self.expiry = tk.Entry(form, bg="gray11", fg="white", insertbackground="white")
        self.expiry.grid(row=2, column=1, pady=5)

        # CVV
        tk.Label(form, text="CVV:", bg="gray17", fg="white")\
            .grid(row=3, column=0, sticky="w", pady=5)
        self.cvv = tk.Entry(form, show="*", bg="gray11", fg="white", insertbackground="white")
        self.cvv.grid(row=3, column=1, pady=5)
        form.columnconfigure(1, weight=1)


    def _on_pay(self):
        name = self.card_name.get()
        number = self.card_number.get()
        expiry = self.expiry.get()
        cvv = self.cvv.get()

        # Basic validation
        if not name:
            messagebox.showerror("Error", "Enter name on card")
            return

        if not number.isdigit() or len(number) != 16:
            messagebox.showerror("Error", "Card number must be 16 digits")
            return

        if len(expiry) != 5 or "/" not in expiry:
            messagebox.showerror("Error", "Use MM/YY format")
            return

        if not cvv.isdigit() or len(cvv) != 3:
            messagebox.showerror("Error", "CVV must be 3 digits")
            return

        user_id = self.master.current_user["user_id"] if self.master.current_user else 1

        try:
            booking = self.booking_service.create_booking(
                user_id=user_id,
                show_id=self.show_id,
                seat_labels=self.selected_seats,
            )
        except Exception as e:
            messagebox.showerror("Booking Error", str(e))
            return

        success, message, data = self.payment_service.make_payment(
            booking_id=booking["booking_id"],
            payment_method="CARD",
            card_number=number,
            card_holder=name,
            expiry_month=int(expiry.split("/")[0]),
            expiry_year=2000 + int(expiry.split("/")[1]),
            cvv=cvv,
        )

        if success:
            booking_details = self.booking_service.get_booking_details(booking["booking_id"])
            self.master.switch_frame(
                BookingConfirmation,
                self.db,
                self.master.current_user,
                booking_details,
                data,
            )
        else:
            messagebox.showerror("Error", message)

    def _back_to_movies(self):
        from src.frontend.customer.customer_window import CustomerWindow
        self.master.switch_frame(CustomerWindow, self.db, self.master.current_user)


class BookingConfirmation(tk.Frame):
    def __init__(self, master, db, user, booking, payment_data):
        super().__init__(master, bg="gray12")
        self.master = master
        self.db = db
        self.user = user
        self.booking = booking
        self.payment_data = payment_data

        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg="gray12", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Booking Confirmed",
                 bg="gray12", fg="sienna1",
                 font=("Helvetica", 20, "bold")).pack(pady=15)

        dtime = datetime.strptime(self.booking["show_datetime"], "%Y-%m-%d %H:%M:%S")
        tk.Label(container, text=f"Movie: {self.booking['movie_title']}",
                 bg="gray12", fg="white",
                 font=("Helvetica", 12)).pack(anchor="w", pady=5)

        tk.Label(container, text=f"Theatre: {self.booking['theatre_name']} ({self.booking['city']})",
                 bg="gray12", fg="white",
                 font=("Helvetica", 12)).pack(anchor="w", pady=5)

        tk.Label(container, text=f"Screen: {self.booking['screen_name']}",
                 bg="gray12", fg="white",
                 font=("Helvetica", 12)).pack(anchor="w", pady=5)

        tk.Label(container, text=f"Showtime: {dtime.strftime('%b %d, %Y - %I:%M %p')}",
                 bg="gray12", fg="white",
                 font=("Helvetica", 12)).pack(anchor="w", pady=5)

        tk.Label(container, text=f"Seats: {', '.join(self.booking['seats'])}",
                 bg="gray12", fg="white",
                 font=("Helvetica", 12)).pack(anchor="w", pady=5)

        tk.Label(container, text=f"Total Paid: ${self.booking['total_amount']:.2f}",
                 bg="gray12", fg="sienna1",
                 font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(10, 15))

        tk.Label(container, text=f"Transaction Ref: {self.payment_data['transaction_ref']}",
                 bg="gray12", fg="white",
                 font=("Helvetica", 10)).pack(anchor="w", pady=5)

        button_frame = tk.Frame(container, bg="gray12")
        button_frame.pack(fill="x", pady=20)

        tk.Button(button_frame, text="View Booking History",
                  bg="sienna1", fg="gray12",
                  font=("Helvetica", 12, "bold"),
                  command=self._view_booking_history).pack(side="left", padx=10)

        tk.Button(button_frame, text="Back to Movies",
                  bg="gray17", fg="white",
                  font=("Helvetica", 12),
                  command=self._back_to_movies).pack(side="left", padx=10)

    def _view_booking_history(self):
        from src.frontend.customer.my_bookings_tab import BookingTab
        self.master.switch_frame(BookingTab, self.db, self.user, None)

    def _back_to_movies(self):
        from src.frontend.customer.customer_window import CustomerWindow
        self.master.switch_frame(CustomerWindow, self.db, self.user)

    