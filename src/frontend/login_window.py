import tkinter as tk
from tkinter import messagebox
from src.backend.services.auth_service import AuthService
"""
    A window to login returning customers.
    This frame allows customers to enter and verify credentials.
    Following verification, customers are then routed to a different
    window.
    Author: D. Tinoco
"""

"""
    A window to login returning customers.
    This frame allows customers to enter and verify credentials.
    Following verification, customers are then routed to a different
    window.
    Author: D. Tinoco
"""
class LoginWindow(tk.Frame):
    """
<<<<<<< HEAD
    The customer window for logging in. The interface allows
    customer to enter username and password, or to select the option to register
    an account.
    """

=======
    The customer window for logging in. The interface allows 
    customer to enter username and password, or to select the option to register
    an account.
    """
>>>>>>> 2cccef9 (added seat picker UI)
    def __init__(self, master, db):
        """
        Constructs/initializes login window.

<<<<<<< HEAD

        Parameters:
            master: Parent Tkinter widget
            db: database controller


        """

=======
        Parameters: 
            master: Parent Tkinter widget
            db: database controller

        """
>>>>>>> 2cccef9 (added seat picker UI)
        super().__init__(master, bg="gray12")
        self.db = db
        self.auth = AuthService(db)
        self._build_ui()
        self.pack(fill="both", expand=True)

    def _build_ui(self):
        """
        Builds a customer login UI.
        Constructs a container, creates additional labels,
        and packs the container with buttons or input boxes
<<<<<<< HEAD
        for respective usernames / passwords.
        """

=======
        for respective usernames / passwords. 
        """
>>>>>>> 2cccef9 (added seat picker UI)
        container = tk.Frame(self, bg="gray12", padx=25, pady=25)
        container.pack(expand=True, padx=40, pady=40)

        tk.Label(container, text=" LOGIN ", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 20, "bold")).pack(pady=(8, 23))

        tk.Label(container, text="EMAIL ADDRESS*", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.username = tk.Entry(container, width=30, bg="gainsboro", borderwidth=0,
                        highlightthickness=1, highlightbackground="gray40")
        self.username.pack(fill="x", pady=(0, 10))

        tk.Label(container, text="PASSWORD*", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.password = tk.Entry(container, width=30, bg="gainsboro", show="*",
                        borderwidth=0, highlightthickness=1, highlightbackground="gray40")
        self.password.pack(fill="x", pady=(0, 10))

        login_button = tk.Button(container, text="LOG IN", bg="sienna1", fg="gray12",
                       font=("Helvetica", 10, "bold"), borderwidth=0, highlightthickness=1,
                       highlightbackground="gray40", command=self._do_login)
        login_button.pack(fill="x", pady=(10, 8))

        tk.Label(container, text="Don't have an account?", bg="gray12", fg="#f5f5f5",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        register_btn = tk.Button(container, text="Create Account", bg="gray12",
                fg="sienna1", font=("Helvetica", 8, "underline"), relief="flat",
                command=self._open_register)
        register_btn.pack(anchor="w", pady=(0, 30))
        register_btn.bind("<Enter>", lambda e: e.widget.config(fg="lightsalmon"))
        register_btn.bind("<Leave>", lambda e: e.widget.config(fg="sienna1"))

    def _do_login(self):
        """
        Validates customer login credentials and leads
        user to alternate window post authentication.
        """
<<<<<<< HEAD

=======
>>>>>>> 2cccef9 (added seat picker UI)
        email = self.username.get().strip()
        password = self.password.get().strip()

        if not email or not password:
            messagebox.showwarning("Login", "Please enter both email and password.")
            return

        user = self.auth.login(email, password)

        if user is None:
            messagebox.showerror("Login Failed", "Invalid email or password.")
            return

        # login successful — destroy this frame and route to correct window
        master = self.master  # save before destroy
        db = self.db          # save before destroy
        user_data = user      # save before destroy
        self.destroy()

        if user["role"] == "customer":
            from .customer.customer_window import CustomerWindow
            CustomerWindow(self.master, self.db, user)
        else:
            from .manager.manager_window import ManagerWindow
            ManagerWindow(self.master, self.db, user)

    def _open_register(self):
        """
        Opens a new window that leads to registration options for
        users who are not returning customers.
        """
<<<<<<< HEAD

=======
>>>>>>> 2cccef9 (added seat picker UI)
        from .registration_window import RegistrationWindow
        master = self.master  # save before destroy
        db = self.db          # save before destroy
        self.destroy()
        RegistrationWindow(self.master, self.db)