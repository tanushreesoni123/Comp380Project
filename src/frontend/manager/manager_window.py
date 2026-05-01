import tkinter as tk

class ManagerReportWindow(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master, bg = "gray12")
        
        self.db = db
        self.pack(fill="both", expand=True)

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Sales Report",
                bg="gray12", fg="sienna1",
                font=("Helvetica", 18, "bold")).pack(pady=20)
        
        #mock data, delete when backend is available
        summary = {
            "total_tickets": 102, 
            "total_revenue": 1450.00,
            "avg_price": 12.00,
            "total_bookings": 85,
            "top_movie": "Interstellar"
        }

        #summary
        summary_frame = tk.Frame(self, bg = "gray12")
        summary_frame.pack(pady = 10)

        tk.Label(summary_frame, text = f"Total Tickets Sold: {summary['total_tickets']}",
                 bg = "gray12", fg = "white", font = ("Helvetica", 12)).pack(pady = 2)
       
        tk.Label(summary_frame, text = f"Total Revenue: {summary['total_tickets']}",
                 bg = "gray12", fg = "white", font = ("Helvetica", 12)).pack(pady = 2)
        
        tk.Label(summary_frame, text = f"Average Ticket Price: {summary['total_tickets']}",
                 bg = "gray12", fg = "white", font = ("Helvetica", 12)).pack(pady = 2)
        
        tk.Label(summary_frame, text = f"Total Bookings: {summary['total_tickets']}",
                 bg = "gray12", fg = "white", font = ("Helvetica", 12)).pack(pady = 2)
        
        tk.Label(summary_frame, text = f"Top Movie: {summary['total_tickets']}",
                 bg = "gray12", fg = "white", font = ("Helvetica", 12)).pack(pady = 2)
        
        #Divider
        tk.Label(self, text = "Movie Breakdown", bg = "gray12", fg = "white",
                 font = ("Helvetica", 16, "bold")).pack(pady = 10)
        
        #mock table data
        movie_data = [
            ("Interstellar", 40, 480),
            ("Howl's Moving Castle", 30, 360),
            ("Spiderverse", 25, 300)
        ]

        table_frame = tk.Frame(self, bg = "gray12")
        table_frame.pack()

        for movie, tickets, revenue in movie_data:
            tk.Label(table_frame,
                    text = f"{movie} - {tickets} - ${revenue}",
                    bg = "gray12", fg = "white",
                    font = ("Helvetica", 11)).pack(anchor="w", pady = 2)
        
        #back button
        tk.Button(self, text = "Back", bg = "gray12", fg = "white",
                  command = lambda: self.master.switch_frame(
                      __import__('src.frontend.login_window', fromList=['LoginWindow']).LoginWindow,
                      self.db
                  )).pack(pady = 20)
    