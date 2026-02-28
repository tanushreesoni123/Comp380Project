import tkinter as tk
from tkinter import ttk, messagebox

from src.backend.database import DB          # ADDED: import DB class from backend
from src.backend.auth_service import AuthService

class App(tk.Tk):
    def __init__(self, db: DB):
        super().__init__()

        # ADDED: these 2 lines connect the frontend to the backend
        self.db = db
        self.auth = AuthService(db)

        self.title("A.D.S.T Movie Booking")
        self.eval('tk::PlaceWindow . center')
        self.configure(bg = "gray12")

        window_width = 600
        window_height = 500

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        style = ttk.Style(self)
        style.theme_use("classic")

        container = tk.Frame(self, bg="gray12", padx=25, pady=25)
        container.pack(expand = True, padx=40, pady=40)

        title = tk.Label(container, text = " LOGIN ", bg = "gray12", fg="#f5f5f5", 
                font = ("Helvetica", 20, "bold"))
        title.pack(pady = (8,23))


        tk.Label(container, text="EMAIL ADDRESS*", bg = "gray12", fg="#f5f5f5",
                font = ("Helvetica", 8, "bold")).pack(anchor = "w")
        self.username = tk.Entry(container, width = 30, bg = "gainsboro", borderwidth=0, 
                        highlightthickness = 1, highlightbackground = "gray40")
        self.username.pack(fill = "x", pady = (0,10))
        
        tk.Label(container, text="PASSWORD*",  bg = "gray12", fg="#f5f5f5", 
                font = ("Helvetica", 8, "bold")).pack(anchor = "w")
        self.password = tk.Entry(container, width = 30, bg = "gainsboro", show = "*", 
                        borderwidth=0, highlightthickness = 1, highlightbackground = "gray40")
        self.password.pack(fill = "x", pady = (0,10))
        
        login_button = tk.Button(container, text = "LOG IN", bg = "sienna1", fg = "gray12", 
                       font = ("Helvetica", 10, "bold"), borderwidth=0, highlightthickness = 1,
                       highlightbackground = "gray40", command = self.login)
        login_button.pack(fill = "x", pady = (10,8))
    


        tk.Label(container, text="Don't have an account?",  bg = "gray12", fg="#f5f5f5",
                font = ("Helvetica", 8, "bold")).pack(anchor = "w")
        createaccount_button = tk.Button(container, text = "Create Account", bg = "gray12",
                fg = "sienna1", font = ("Helvetica", 8, "underline"), relief = "flat", 
                command = lambda: None) # MODIFIED: was self.login, now self.open_register
        createaccount_button.pack(anchor = "w", pady = (0, 30))
        createaccount_button.bind("<Enter>", self.on_enter)
        createaccount_button.bind("<Leave>", self.on_leave)


    def on_enter(self, e):
         e.widget.config(fg = "lightsalmon")


    def on_leave(self, e):
         e.widget.config(fg = "sienna1") 

    def login(self):
        email = self.username.get().strip()    # <-- MODIFIED: was username = self.username.get()
        password = self.password.get().strip() # <-- MODIFIED: was password = self.password.get()

        # <-- ADDED: empty field check
        if not email or not password:
            messagebox.showwarning("Login", "Please enter both email and password.")
            return

        # MODIFIED: was print("Login attempted:", username)
        # now actually calls backend to validate credentials
        user = self.auth.login(email, password)

        if user is None:
            messagebox.showerror("Login Failed", "Invalid email or password.")
        else:
            messagebox.showinfo("Login Successful", f"Welcome, {user['name']}!\nRole: {user['role']}")

if __name__ == "__main__":
    from src.backend.database import DB, init_db
    db = DB("movies.db")
    init_db(db)
    app = App(db)
    app.mainloop()
    db.close()
