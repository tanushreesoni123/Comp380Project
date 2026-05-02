import tkinter as tk
from src.frontend.login_window import LoginWindow
from src.backend.services.report_service import ReportService
class ManagerReportWindow(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master, bg = "gray12")
        
        self.db = db
        self.pack(fill="both", expand=True)
        self.report_service = ReportService(self.db)

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Sales Report",
                bg="gray12", fg="sienna1",
                font=("Helvetica", 18, "bold")).pack(pady=20)
        
        try:
            total_revenue = self.report_service.get_total_revenue()
            total_bookings = self.report_service.get_total_bookings()
            popular_movies = self.report_service.get_popular_movies()
            revenue_per_movie = self.report_service.get_revenue_per_movie()

        except Exception as e:
           print("Report Error:", e)
           total_revenue = 0
           total_bookings = 0
           popular_movies = []
           revenue_per_movie = [] 

        #summary
        tk.Label(self, text = f"Total Bookings: {total_bookings}",
                 bg = "gray12", fg = "white").pack(pady = 5)
       
        tk.Label(self, text = f"Total Revenue: ${total_revenue:.2f}",
                 bg = "gray12", fg = "white").pack(pady = 5)
        
        tk.Label(self, text = "Most Popular Movies",
                 bg = "gray12", fg = "white", font = ("Helvetica", 14, "bold")).pack(pady = 10)
        
        for movie in popular_movies:
            tk.Label(self, text = f"{movie['movie_title']} - {movie['total_bookings']} bookings",
                     bg = "gray12", fg = "white").pack(anchor = "w")
            
        
        tk.Label(self, text = "Revenue by Movie", bg = "gray12", fg = "sienna1",
                 font = ("Helvetica", 14, "bold")).pack(pady = 10)
        
        for movie in revenue_per_movie:
            tk.Label(self, text = f"{movie['movie_title']} - ${movie['revenue']:.2f}",
                     bg = "gray12", fg = "white").pack(anchor = "w")
        #back button
        tk.Button(self, text = "Back", bg = "gray12", fg = "white",
                  command = lambda: self.master.switch_frame(LoginWindow,self.db
                  )).pack(pady = 20)
    