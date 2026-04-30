#commented out all code prior to backend connection
#UI is functional, I had hardcoded everything, but was unable
#to connect to backend, so I commented out the code
#so that everyone could see my logic 

"""
import tkinter as tk


from datetime import datetime
from src.backend.services.booking_service import BookingService

#commented all lines of code with variables like movie/
#theatre_name, screen_name, city, etc. 
#need to use finalized backend to implement frontend properly


class BookingCard(tk.Frame):
    def __init__(self, parent, booking, on_click):

        super().__init__(parent, bg = "gray21", padx = 10, pady = 10)


        self.booking = booking
        self.on_click = on_click
        self.parent = parent

        #defines different text inputs so that they can be used with buttons easily
        dtime = datetime.strptime(self.booking["show_datetime"], "%Y-%m-%d %H:%M:%S")
        all_seat_labels = ", ".join(self.booking["seat_labels"])

        current_booking_status = " "
        if self.booking["status"] == "CANCELED":
            current_booking_status = "| CANCELED"



        button_text = (
            f"{self.booking['title']} {current_booking_status}\n"
            f"{dtime.strftime('%b %d, %Y - %I:%M%p ')} \n"
            f"{self.booking['theatre_name']} | {self.booking['city']} \n"
            f"Seats: {all_seat_labels}\n"
            f"#{self.booking['booking_id']}"
        )


        self.booking_button = tk.Button(self, text = button_text, bg = "gray21", fg = "gray87",
            font = ("Helvetica", 14, "bold"), justify = "left", anchor = "center", command = self.handle_click)


        self.booking_button.pack(fill = "x")

        self.booking_button.bind("<Enter>", self.on_enter)
        self.booking_button.bind("<Leave>", self.on_leave)


    def handle_click(self):
        self.on_click(self.booking)


    def on_enter(self, event):
        self.booking_button.config(bg="sienna1")


    def on_leave(self, event):
        self.booking_button.config(bg="gray27")


class BookingTab(tk.Frame):
    def __init__(self, parent, db, user, on_return):


        super().__init__(parent, bg = "gray20")
        self.parent = parent
        self.db = db
        self.user = user
        self.on_return = on_return


        self.parent.eval('tk::PlaceWindow . center')
        self.booking_service = BookingService(self.db)


        window_width = 1000
        window_height = 800


        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()


        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))


        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.pack(fill = "both", expand = True)


        self.build_ui()


    def build_ui(self):
        self.configure(bg = "gray20")

        #makes the top of the booking tab (for the title)
        self.top = tk.Frame(self, bg = "gray20")
        self.top.pack(fill = "x", padx = (20,20))


        self.bookings_title = tk.Label(self.top, text = "Booking History", bg = "gray20",
                                    fg = "gray87", font = ("Helvetica", 27, "bold"))
        self.bookings_title.pack(anchor = "n", padx = 10, pady = 20)


        #a container to hold all of the different bookings (and making it scrollable)
        booking_list_container = tk.Frame(self, bg=  "gray20")
        booking_list_container.pack(expand = True, fill = "both", padx=40, pady=20)

        self.canvas = tk.Canvas(booking_list_container, bg = "gray20", highlightthickness = 0, bd = 0)
        self.canvas.pack(side = "left", fill = "both", expand = True)

        scrollbar = tk.Scrollbar(booking_list_container, orient = "vertical",
                                 command = self.canvas.yview, width = 20, activebackground = "sienna1",
                                 troughcolor = "gray7")
        scrollbar.pack(side = "right", fill = "y", padx = 3)


        self.canvas.configure(yscrollcommand=scrollbar.set)


        self.scrollable_frame = tk.Frame(self.canvas, bg="gray20")
        self.canvas_window = self.canvas.create_window((0,0), window = self.scrollable_frame, anchor = "nw")


        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.new_scroll_frame)


        #makes a smaller frame for buttons 
        self.bottom = tk.Frame(self, bg = "gray20")
        self.bottom.pack(fill = "x", padx = 40, pady = 5, side = "bottom")


        self.return_button = tk.Button(self.bottom, text = "Return to Movies", bg = "sienna1", fg = "gray12",
                      font =("Helvetica", 12),
                     highlightbackground = "gray25", height = 3, width = 14, command = self.return_to_movies)


        self.return_button.pack(side = "right", padx = 20, pady=10)

        self.canvas.bind("<Enter>", self.bind_to_mousewheel)
        self.canvas.bind("<Leave>", self.unbind_to_mousewheel)


        bookings = []
        booking_rows = self.booking_service.get_user_bookings(self.user["user_id"])

        for booking in booking_rows:
            extra_info = self.booking_service.get_booking_details(booking["booking_id"])

            bookings.append({
                "booking_id": booking["booking_id"],
                "user_id" : booking["user_id"],
                "show_id" : booking["show_id"], 
                "booking_time": booking["booking_time"], 
                "total_amount" : booking["total_amount"],
                "status" : booking["status"],
                "cancel_time" : booking["cancel_time"],
                "title" : extra_info["movie_title"],
                "show_datetime" : extra_info["show_datetime"],
                "seat_labels" : extra_info["seats"]
            })
    
    
        #loops through our bookings to make an individual card/booking for each

        for booking in bookings:
            card = BookingCard(self.scrollable_frame, booking, self.select_booking)
            card.pack(fill = "x", padx = (10,20), pady = 10)

    #refreshes in the case that a booking is canceled 
    def refresh_bookings(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()


    def new_scroll_frame(self, event):
        self.canvas.itemconfig(self.canvas_window, width = event.width-12)

    #takes you to the popup receipt 
    def select_booking(self, booking):
        TicketPopup(self.master, self.db, self.user, booking, on_return = self.refresh_bookings)

    #takes you back to available movie window
    def return_to_movies(self):
        if self.on_return:
            self.destroy()
            from .customer.customer_window import CustomerWindow
            CustomerWindow(self.master, self.db, self.user)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def unbind_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")



class TicketPopup(tk.Toplevel):
    def __init__(self, parent, db, user, booking, on_return = None):
        super().__init__(parent, bg = "gray25")
        self.parent = parent
        self.db = db
        self.user = user
        self.booking = booking
        self.on_return = on_return
       


        #self.booking_service = BookingService(self.db)
        self.title(f"#{booking['booking_id']}")
        self.geometry("650x850")
        self.configure(bg = "snow2")


        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (850 // 2)
        self.geometry(f"+{x}+{y}")
       
        self.main_frame = tk.Frame(self, bg="snow2")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
       
        self.build_ui()


    def build_ui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


        self.top = tk.Frame(self, bg = "snow2")
        self.top.pack(fill = "x", padx = (20,20))    


        dtime = datetime.strptime(self.booking["show_datetime"], "%Y-%m-%d %H:%M:%S")

        refund_text = ""
        #want to update a receipt in the case that booking status changes
        if self.booking["status"] == "CANCELED":
            refund_text = " | CANCELED"


        ticket_text_top = (
            f"{self.booking['title']} {refund_text}\n "
            f"{self.booking['theatre_name']} | {self.booking['city']} | "
            f"{self.booking['screen_name']}\n "
            f"#{self.booking['booking_id']}\n"
            f"{dtime.strftime('%b %d, %Y - %I:%M %p')}"
            )

        #frames general ticket info
        self.booking_info = tk.Label(self.top, text = ticket_text_top, bg = "snow2", fg = "gray7",
                            font =("Times", 17, "bold"), wraplength = 500)
        self.booking_info.pack(side = "top", anchor = "n", padx = 50, pady = 20)

        #frames ticket quantity/seats
        self.booked_tickets_container = tk.Frame(self, bg=  "snow2")
        self.booked_tickets_container.pack(expand = True, fill = "y", padx=50, pady=20)


        num_tickets = len(self.booking["seat_labels"])
        all_seats = ", ".join(self.booking["seat_labels"])
        

        num_tickets_label = tk.Label(self.booked_tickets_container, text = f"{num_tickets}x  -  Tickets", bg = "snow2", fg = "gray7",
            font = ("Times", 18, "bold") )
        num_tickets_label.grid(row = 0, column = 1, sticky = "w", pady = 5)

        listed_seats_label = tk.Label(self.booked_tickets_container, text = f"\t - Seats: {all_seats}", bg = "snow2", fg = "gray7",
            font = ("Times", 18), wraplength = 500 )
        listed_seats_label.grid(row = 1, column = 1, sticky = "w", pady = (5, 30))

        subtotal_label = tk.Label(self.booked_tickets_container, text = f"Subtotal: \t\t ${self.booking['total_amount']:.2f}", bg = "snow2", fg = "gray7",
            font = ("Times", 18, "bold"))
        subtotal_label.grid(row = 2, column = 1, sticky = "w", pady = 10)

        


        #Sectioning off the bottom to display needed buttons
        self.ticket_bottom = tk.Frame(self, bg = "snow2")
        self.ticket_bottom.pack(expand = True, fill = "both", padx = 50, pady = 20)

        #allows you to cancel bookings only if you cancel before showtime 
        #and if you haven't already canceled your booking
        
        if datetime.now() < dtime and self.booking["status"] == "CONFIRMED":


            self.return_to_bookings_button = tk.Button(self.ticket_bottom, text = "Return", bg = "sienna1", fg = "gray7",
                font =("Helvetica", 12), highlightbackground = "gray25", height = 3, width = 14, command = self.return_to_booking)

            self.return_to_bookings_button.pack(side = "left", padx = 20, pady=10)

            self.cancel_booking_button = tk.Button(self.ticket_bottom, text = "Cancel Booking", bg = "sienna1", fg = "gray7",
                      font =("Helvetica", 12), highlightbackground = "gray25", height = 3, width = 14, command = self.cancel_booking)

            self.cancel_booking_button.pack(side = "right", padx = 20, pady=10)

        else: 
            self.return_to_bookings_button = tk.Button(self.ticket_bottom, text = "Return", bg = "sienna1", fg = "gray7",
                font =("Helvetica", 12), highlightbackground = "gray25", height = 3, width = 12, command = self.return_to_booking)

            self.return_to_bookings_button.pack(anchor = "center", padx = 20, pady=10)



    #takes you back to booking history
    def return_to_booking(self):
        if self.on_return:
            self.destroy()
            self.on_return()

    #takes you to a new popup window to CONFIRM you want to cancel 
    def cancel_booking(self):
        CancelBooking(self, self.db, self.user, self.booking, on_approve = self.after_cancel)

    #if you have canceled, window gets closed 
    def after_cancel(self):
        self.booking["status"] = "CANCELED"
        self.booking["cancel_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.destroy()

        if self.on_return:
            self.on_return()


class CancelBooking(tk.Toplevel):
    def __init__(self, parent, db, user, booking, on_approve):
        super().__init__(parent, bg = "gray25")

        self.parent = parent
        self.db = db
        self.user = user
        self.booking = booking
        self.on_approve = on_approve

        self.title("Cancel Booking")
        self.geometry("700x550")
        self.configure(bg = "gray20")


        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"+{x}+{y}")
       
        self.main_frame = tk.Frame(self, bg="gray20")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
       
        self.build_ui()

    def build_ui(self):

        for widget in self.main_frame.winfo_children():
            widget.destroy()


        self.middle = tk.Frame(self.main_frame, bg = "gray20")
        self.middle.pack(expand = True, pady = 20)
  


        self.cancellation = tk.Label(self.middle, text = "Cancel Booking?", bg = "gray20", fg = "white",
                            font =("Helvetica", 25, "bold"))
        self.cancellation.pack(pady = (30,10))

        self.confirmation_question = tk.Label(self.middle, text = "You will not be able to undo cancellation.", bg = "gray20", fg = "white",
                            font =("Helvetica", 15, "bold"))
        self.confirmation_question.pack(pady = (5, 20))



        button_section = tk.Frame(self.middle, bg = "gray20")
        button_section.pack(pady = 10)

        self.back_to_bookings_button = tk.Button(button_section, text = "Return", bg = "sienna1", fg = "gray12",
                font =("Helvetica", 12), highlightbackground = "gray20", height = 2, width = 14, command = self.back_to_booking)

        self.back_to_bookings_button.pack(side = "left", padx = 20, pady=10)

        self.finalize_cancellation_button = tk.Button(button_section, text = "Cancel Booking", bg = "sienna1", fg = "gray12",
                      font =("Helvetica", 12), highlightbackground = "gray20", height = 2, width = 14, command = self.final_cancel)

        self.finalize_cancellation_button.pack(side = "right", padx = 20, pady=10)


    def back_to_booking(self):
            self.destroy()

    #updates booking status 
    def final_cancel(self):
        self.booking["status"] = "CANCELED"
        self.booking["cancel_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.on_approve:
            self.on_approve()

        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("BookingTabWindow")
    fake_db = None
    fake_user = {"user_id":1, "name" : "dt"}
    app = BookingTab(root, fake_db, fake_user, on_return = None)
    root.mainloop()



