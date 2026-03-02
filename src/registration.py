import tkinter as tk


class RegistrationWindow(tk.Toplevel):

    def __init__(self, parent: tk.Tk | tk.Toplevel):
        super().__init__(parent)

        # Basic window setup 
        self.title("Create Account")
        self.configure(bg="gray12")

        # Center window on the screen 
        window_width = 600
        window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        container = tk.Frame(self, bg="gray12", padx=25, pady=25)
        container.pack(expand=True, padx=40, pady=40)

        title = tk.Label(
            container,
            text=" CREATE ACCOUNT ",
            bg="gray12",
            fg="#f5f5f5",
            font=("Helvetica", 20, "bold"),
        )
        title.pack(pady=(8, 23))

        # Name
        tk.Label(
            container,
            text="FULL NAME*",
            bg="gray12",
            fg="#f5f5f5",
            font=("Helvetica", 8, "bold"),
        ).pack(anchor="w")
        self.name_entry = tk.Entry(
            container,
            width=30,
            bg="gainsboro",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="gray40",
        )
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Email
        tk.Label(
            container,
            text="EMAIL ADDRESS*",
            bg="gray12",
            fg="#f5f5f5",
            font=("Helvetica", 8, "bold"),
        ).pack(anchor="w")
        self.email_entry = tk.Entry(
            container,
            width=30,
            bg="gainsboro",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="gray40",
        )
        self.email_entry.pack(fill="x", pady=(0, 10))

        # Password
        tk.Label(
            container,
            text="PASSWORD*",
            bg="gray12",
            fg="#f5f5f5",
            font=("Helvetica", 8, "bold"),
        ).pack(anchor="w")
        self.password_entry = tk.Entry(
            container,
            width=30,
            bg="gainsboro",
            show="*",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="gray40",
        )
        self.password_entry.pack(fill="x", pady=(0, 10))

        # Confirm password
        tk.Label(
            container,
            text="CONFIRM PASSWORD*",
            bg="gray12",
            fg="#f5f5f5",
            font=("Helvetica", 8, "bold"),
        ).pack(anchor="w")
        self.confirm_entry = tk.Entry(
            container,
            width=30,
            bg="gainsboro",
            show="*",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="gray40",
        )
        self.confirm_entry.pack(fill="x", pady=(0, 10))

        # Error / info label
        self.message_label = tk.Label(
            container,
            text="",
            bg="gray12",
            fg="tomato",
            font=("Helvetica", 8, "bold"),
        )
        self.message_label.pack(anchor="w", pady=(0, 8))

        # Buttons row
        button_row = tk.Frame(container, bg="gray12")
        button_row.pack(fill="x", pady=(10, 0))

        create_btn = tk.Button(
            button_row,
            text="CREATE ACCOUNT",
            bg="sienna1",
            fg="gray12",
            font=("Helvetica", 10, "bold"),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="gray40",
            command=self.on_create_account,
        )
        create_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        cancel_btn = tk.Button(
            button_row,
            text="CANCEL",
            bg="gray25",
            fg="#f5f5f5",
            font=("Helvetica", 9, "bold"),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="gray40",
            command=self.destroy,
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

    def on_create_account(self) -> None:
       
        #Basic validation + placeholder behavior

        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not name or not email or not password or not confirm:
            self.message_label.config(text="Please fill in all required fields.")
            return

        if password != confirm:
            self.message_label.config(text="Passwords do not match.")
            return

        # temporary, just print to the console and close.
        print("Registration submitted:", name, email)
        self.message_label.config(text="Account created.")
        self.after(700, self.destroy)


def open_registration(parent: tk.Tk | tk.Toplevel) -> None:
    
    #Helper that  can be called from the login screen, without editing login file.

    RegistrationWindow(parent)


if __name__ == "__main__":
    # Allow to run just the registration window for testing,
    # without starting the rest of the app.
    root = tk.Tk()
    root.withdraw()  # hide the root window
    RegistrationWindow(root)
    root.mainloop()

