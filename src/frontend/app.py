import tkinter as tk
from tkinter import ttk
from src.backend.database import DB
from .login_window import LoginWindow

class App(tk.Tk):
    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.current_user = None  # Track current logged-in user

        self.title("A.D.S.T Movie Booking")
        self.configure(bg="gray12")

        window_width = 600
        window_height = 500

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        style = ttk.Style(self)
        style.theme_use("classic")

        # NEW: track current screen
        self.current_frame = None

        # Start with login
        self.switch_frame(LoginWindow, self.db)

    # added this to switch between frames
    def switch_frame(self, frame_class, *args):
        print("Switching to:", frame_class)

        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame_class(self, *args)
        self.current_frame.pack(fill="both", expand=True)