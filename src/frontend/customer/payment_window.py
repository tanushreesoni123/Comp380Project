import tkinter as tk
from tkinter import messagebox
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

        self.db = DB("movies.db")
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

        tk.Button(container,
                  text="Pay Now",
                  bg="sienna1", fg="gray12",
                  command=self._on_pay).pack(pady=20)
        form = tk.Frame(container, bg="gray17", padx=10, pady=10)
        ##just added
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

        ## just added

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

        # TEMP (replace with backend later)
        messagebox.showinfo("Success", "Payment processed!")
        
        # Get user_id from current user
        user_id = self.master.current_user["user_id"] if self.master.current_user else 1
        
        success, message, data = self.payment_service.make_payment(
            user_id=user_id,
            show_id=self.show_id,
            seat_labels=self.selected_seats,
            payment_method="CARD",
            card_number="1234567812345678",
            card_holder="Test User",
            expiry_month=12,
            expiry_year=2026,
            cvv="123"
        )


        if success:
            messagebox.showinfo("Success", f"Booking confirmed!\nRef: {data['transaction_ref']}")
            self.window.destroy()
        else:
            messagebox.showerror("Error", message)

    