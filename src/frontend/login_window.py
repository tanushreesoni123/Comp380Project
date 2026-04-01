import tkinter as tk
from tkinter import messagebox
from src.backend.services.auth_service import AuthService

class LoginWindow(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master, bg="gray12")
        self.db = db
        self.auth = AuthService(db)
        self._build_ui()
        self.pack(fill="both", expand=True)

    def _build_ui(self):
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
        from .registration_window import RegistrationWindow
        master = self.master  # save before destroy
        db = self.db          # save before destroy
        self.destroy()
        RegistrationWindow(self.master, self.db)