import tkinter as tk
from tkinter import messagebox
from src.backend.services.auth_service import AuthService


class RegistrationWindow(tk.Frame):
    
    """
    Class Name: RegistrationWindow
    Date: 04-16-2026
    Programmer: Allison Berkeland

    Description: This class creates the user registration interface
    for the movie booking application. It allows for new users to input 
    their name, email, and password to create an account. The class also 
    handles frontend validation and communicates with the backend authentication
    to register the user.

    Functions:
    - _build_ui(): Constructs the registration form UI elements.
    - _do_register(): Handles the validity of the user input and registration logic
    - _go_back(): Sends the user back to the login screen       

    Inputs:
    - master: parent window/frame
    - db: database connection object for authentication

    Outputs:
    - None (GUI-based interactions)

    Data Structures:
    - Uses Tkinter widgets to collect user input
    - Uses strings to store user information (name, email, password)

    Algorthims:
    - Input validation:
        - Check for empty fields
        - Check if password and confirm password match
    """


    def __init__(self, master, db):

        """
        Initializes the registration window and sets up dependencies.

        """
        super().__init__(master, bg="gray12")
        self.db = db
        self.auth = AuthService(db)
        self._build_ui()
        self.pack(fill="both", expand=True)

    def _build_ui(self):
        """
        Builds the user interface for the registration form, including
        input fields, buttons, labels, and error message display.
        """
        container = tk.Frame(self, bg="gray12", padx=25, pady=25)
        container.pack(expand=True, padx=40, pady=40)

        tk.Label(container, text=" CREATE ACCOUNT ", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 20, "bold")).pack(pady=(8, 23))

        # Name
        tk.Label(container, text="FULL NAME*", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.name_entry = tk.Entry(container, width=30, bg="gainsboro", borderwidth=0,
                        highlightthickness=1, highlightbackground="gray40")
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Email
        tk.Label(container, text="EMAIL ADDRESS*", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.email_entry = tk.Entry(container, width=30, bg="gainsboro", borderwidth=0,
                        highlightthickness=1, highlightbackground="gray40")
        self.email_entry.pack(fill="x", pady=(0, 10))

        # Password
        tk.Label(container, text="PASSWORD*", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.password_entry = tk.Entry(container, width=30, bg="gainsboro", show="*",
                        borderwidth=0, highlightthickness=1, highlightbackground="gray40")
        self.password_entry.pack(fill="x", pady=(0, 10))

        # Confirm password
        tk.Label(container, text="CONFIRM PASSWORD*", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.confirm_entry = tk.Entry(container, width=30, bg="gainsboro", show="*",
                        borderwidth=0, highlightthickness=1, highlightbackground="gray40")
        self.confirm_entry.pack(fill="x", pady=(0, 10))

        # inline error label — better UX than a popup for form errors
        self.message_label = tk.Label(container, text="", bg="gray12", fg="tomato",
                font=("Helvetica", 8, "bold"))
        self.message_label.pack(anchor="w", pady=(0, 8))

        # Buttons
        button_row = tk.Frame(container, bg="gray12")
        button_row.pack(fill="x", pady=(10, 0))

        tk.Button(button_row, text="CREATE ACCOUNT", bg="sienna1", fg="gray12",
                font=("Helvetica", 10, "bold"), borderwidth=0, highlightthickness=1,
                highlightbackground="gray40",
                command=self._do_register).pack(side="left", fill="x", 
                expand=True, padx=(0, 6))

        tk.Button(button_row, text="CANCEL", bg="gray25", fg="#f5f5f5",
                font=("Helvetica", 9, "bold"), borderwidth=0, highlightthickness=1,
                highlightbackground="gray40",
                command=self._go_back).pack(side="left", fill="x", 
                expand=True, padx=(6, 0))

    def _do_register(self):
        """
        Handles the registration process.

        Steps:
        1. Retrive user input from entry fields.
        2. Perform frontend validation (empty fields, passwords match)
        3. Call backend authentication service.
        4. Display success or error messages.
        """

        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        # frontend validation first — before hitting the backend
        if not name or not email or not password or not confirm:
            self.message_label.config(text="Please fill in all required fields.")
            return

        if password != confirm:
            self.message_label.config(text="Passwords do not match.")
            return

        # now call the backend
        ok, msg = self.auth.register(name, email, password)

        if ok:
            messagebox.showinfo("Success", "Account created! Please log in.")
            self._go_back()
        else:
            # show backend error inline e.g. "Email already exists"
            self.message_label.config(text=msg)

    def _go_back(self):
        """
        Returns the user to login screen.
        Destroys the current window and initializes the login interface.
        """
        # go back to login screen
        from .login_window import LoginWindow
        master = self.master
        db = self.db
        self.destroy()
        LoginWindow(master, db)