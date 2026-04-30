import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


#from src.backend.database import DB
from src.backend.services.booking_service import BookingService


class MovieSeat:


    def __init__(self, seat_id, row, num, availability = "available"):
        self.seat_id = seat_id
        self.row = row
        self.num = num
        self.availability = availability
        self.button = "None"




class SeatPicker(tk.Toplevel):
    def __init__(self, master, db, user, movie, show):
        super().__init__(master, bg = "gray12")
        self.master = master
        self.db = db
        self.user = user
        self.movie = movie
        self.show = show
        self.seats = {}
        self.selected_seat_list = []
        self.booking_service = BookingService(self.db)
        self.taken_seats = self.booking_service.get_taken_seats(self.show["show_id"])

        window_width = 1000
        window_height = 800


        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()


        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))


        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        #self.pack(fill = "both", expand = True)
        self.title(f"{movie['title']} - Select Seats")
        self.configure(bg = "gray12")




        self.seat_layout = self.build_seat_layout()

        self.max_columns = max(self.seat_layout.values())
        self.build_ui()
        self.create_seat()


    def build_ui(self):


        #separates top (for a title + return button)
        self.top = tk.Frame(self, bg = "gray10")
        self.top.pack(fill = "x", padx = (20,20))


        self.return_button = tk.Button(self.top, text = "Return", bg = "gray10", fg = "white", relief = "flat",
                            font =("Helvetica", 8, "bold"), height = 2, width = 5, command = self.return_to_showtime)


        self.return_button.pack(side = "left", padx = 10, pady=10)


        self.screen_title = tk.Label(self.top, text = "SCREEN", bg = "gray10", fg = "white",
                            font =("Helvetica", 30, "bold"))
        self.screen_title.pack(side = "top", anchor = "n", padx = 10, pady = 20)

        dtime = datetime.strptime(self.show["show_datetime"], "%Y-%m-%d %H:%M:%S")
        self.details_label = tk.Label(self.top,
            text = (f"{self.movie['title']} | " 
                    f"{self.show['theatre_name']} | " 
                    f"{self.show['screen_name']} | "
                    f"{dtime.strftime('%b %d, %Y - %I:%M %p')}"), bg = "gray10", 
                    fg = "sienna1", font = ("Helvetica", 12, "bold")
                    #f"{showtime['screen_name']} | ${showtime['base_price']:.2f}"
            )
        self.details_label.pack(side = "top", pady = (5,10))


        #a container to center and place the seats in the middle of the window
        self.seats_container = tk.Frame(self, bg = "gray10")
        self.seats_container.pack(expand = True, fill = "both", padx = 40, pady = 20)
        self.seats_center = tk.Frame(self.seats_container, bg = "gray10")
        self.seats_center.pack(expand = True)

        #the bottom to show details
        self.bottom = tk.Frame(self, bg = "gray10")
        self.bottom.pack(expand = True, fill = "both", padx = 40, pady = 20)


        self.checkout_list = tk.Label(self.bottom, text = "Selected Seats: None\n Total: $0.00", bg = "gray10", fg = "white",
                            font =("Helvetica", 15, "bold"), wraplength = 600, justify = "left")
        self.checkout_list.pack(side = "left", padx = (20,20))




        self.next_button = tk.Button(self.bottom, text = "Next", bg = "sienna1", fg = "gray12",
                      font =("Helvetica", 12, "bold"),
                     highlightbackground = "gray20", height = 2, width = 8, command = self.checkout)


        self.next_button.pack(side = "right", padx = 20, pady=10)

    #connects frontend to backend
    def build_seat_layout(self):
        layout = {}
        all_rows = self.show["rows"]
        all_columns = self.show["cols"]

        for row in range(all_rows):
            row_index = chr(ord("A") + row)
            layout[row_index] = all_columns

        return layout




    def clicked_seat(self, seat_id):
        seat = self.seats[seat_id]

        if seat.availability == "taken":
            return

        #allows you to select seats
        if seat.availability == "available":
            seat.availability = "selected"
            seat.button.config(bg = "sienna1", fg = "gray10")
            self.selected_seat_list.append(seat_id)

        #allows you to deselect seats
        elif seat.availability == "selected":
            seat.availability = "available"
            seat.button.config(bg = "gray20", fg = "white")
            self.selected_seat_list.remove(seat_id)
           


        self.update_checkout_list()



    #creates our seat buttons
    def create_seat(self):
        for row_index, (row, seat_total) in enumerate(self.seat_layout.items()):


            center = (self.max_columns - seat_total) // 2
            for seat_num in range(1, seat_total +1):
                seat_id = f"{row}{seat_num}"
                seat = MovieSeat(seat_id, row, seat_num)

                seat_taken = seat_id in self.taken_seats

                #a button for each seat, enumerates a list to identify seat
                seat_button = tk.Button(self.seats_center, text = seat_id, bg = "gray20",
                        fg = "white", height = 3, width = 6,
                        command = lambda e = seat_id: self.clicked_seat(e))

                if seat_taken:
                    seat.availability = "taken"
                    seat_button.config(bg = "firebrick4", fg = "white", state = "disabled")

                else: 
                    seat_button.config(bg = "gray20", fg = "white",  height = 3, width = 6,
                        command = lambda e = seat_id: self.clicked_seat(e))

                seat_button.grid(row = row_index, column = center + (seat_num -1), padx = 4, pady = 3)
                seat.button = seat_button
                self.seats[seat_id] = seat

    #updates list at the bottom of window
    def update_checkout_list(self):
        if self.selected_seat_list:
            text = ", ".join(self.selected_seat_list)
       
        else:
            text = "None"

        total = len(self.selected_seat_list) * float(self.show["base_price"])
        self.checkout_list.configure(text = f"Selected Seats: {text}\nTotal: ${total:.2f}")


    def checkout(self):
        print("Done")


    def return_to_showtime(self):
        self.master.deiconify()
        self.destroy()


