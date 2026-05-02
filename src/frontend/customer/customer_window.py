import tkinter as tk
#from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from datetime import datetime

from src.backend.services.movies_service import MovieService
#from src.backend.database import DB
from src.frontend.customer.seat_picker import SeatPicker 

"""
    The customer window for browsing available movies.
    This frame allows customers to view movie posters,
    titles, and descriptions. It also allows movie
    selection through the UI.
    Author: D. Tinoco


"""


class CustomerWindow(tk.Frame):
    """
    The primary customer window for browsing available movies.
    The interface is scrollable, displays movie details, and permits
    movie selection.
    """

    
    def __init__(self, master, db, user):
        """
        Constructs/initializes the customer window.


        Parameters:
            master: Parent Tkinter widget
            db: Database connector
            user: Current user
        """

        super().__init__(master, bg = "gray12")

        self.db =db
        self.user = user
        self.master.eval('tk::PlaceWindow . center')
        self.movies_service = MovieService(self.db)
        self.configure(bg = "gray12")

        #wanted a bigger window display
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
        """
        Builds the movie browsing UI.


        Constructs the outer container, canvas,
        scrollbar, and the frame that can be scrolled through
        to show the available movies/movie cards.


        """

        self.configure(bg = "gray12")
        self.top = tk.Frame(self, bg = "gray12")
        self.top.pack(fill = "x", padx = 20)

        self.available_movies = tk.Label(self.top, text = "Now Playing", bg = "gray12",
                                    fg = "white", font = ("Helvetica", 17, "bold"))
        self.available_movies.pack(anchor = "n", padx = 10, pady = 10)


        movie_list_container = tk.Frame(self, bg=  "gray13")
        movie_list_container.pack(expand = True, fill = "both", padx=10, pady=20)

        self.canvas = tk.Canvas(movie_list_container, bg = "gray13", highlightthickness = 0, bd = 0)
        self.canvas.pack(side = "left", fill = "both", expand = True)

        scrollbar = tk.Scrollbar(movie_list_container, orient = "vertical",
                                 command = self.canvas.yview)
        scrollbar.pack(side = "right", fill = "y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas, bg="gray12")
        self.canvas_window = self.canvas.create_window((0,0), window = self.scrollable_frame, anchor = "nw")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.new_scroll_frame)

        movie_rows = self.movies_service.get_all_movies()

        self.canvas.bind("<Enter>", self.bind_to_mousewheel)
        self.canvas.bind("<Leave>", self.unbind_to_mousewheel)



        #movie titles + poster storage
        all_posters ={
            "Interstellar" : "assets/movieposters/Interstellar.png",
            "Arrival" : "assets/movieposters/Arrival.png",
            "Hacksaw Ridge" : "assets/movieposters/HacksawRidge.png", 
            "Across the Spiderverse" : "assets/movieposters/AcrossTheSpiderverse.png",
            "The Maze Runner" : "assets/movieposters/TheMazeRunner.png",
            "Howl's Moving Castle" : "assets/movieposters/HowlsMovingCastle.png"
            }
        
        movies = []

        for movie in movie_rows:
            movies.append({
                "movie_id" : movie["movie_id"], "title" : movie["title"],
                "genre" : movie["genre"], "language" : movie["language"],
                "duration_min" : movie["duration_min"],
                "description" : movie["synopsis"],
                "image" : all_posters.get(movie["title"], "assets/movieposters/default.png")
            })

        #creates a movie card/slot in our layout for each movie
        for movie in movies:
            card = MovieCard(self.scrollable_frame, movie, on_click = self.select_movie)
            card.pack(fill="x", padx=10, pady=10)

    def new_scroll_frame(self,event):
        """
        Alters the scrollable frame to fit the canvas window and width size.
        Parameters:
            event: Tkinter configuring event

        """
        self.canvas.itemconfig(self.canvas_window, width = event.width-12)


    #to ensure our button/movie can be selected
    def select_movie(self, movie):
        """
        A tester method to show that the button is functioning
        """

        ShowtimePopup(self.master, self.db, self.user, movie)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "pages")

    def bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def unbind_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

#creates various cards using images/title (they're buttons that can be clicked on)
class MovieCard(tk.Frame):
    """
    The UI that represents / stores individual movie cards. Each
    movie card includes a poster, title, and description. Each is clickable
    to enable movie selection.
    Author: D. Tinoco
    """

    def __init__(self, parent, movie, on_click):
        """
        Initializes a movie card


        Parameters:
            parent: Parent Tkinter widget
            movie: dictionary containing movie info
            on_click: A function that is called when movie card is selected
        """

        super().__init__(parent, bg = "gray17", padx = 10, pady = 10)
         
        self.movie = movie
        self.on_click = on_click
        im = Image.open(movie["image"])
        im = im.resize((120, 150) )
        self.photo = ImageTk.PhotoImage(im)

        self.image_button = tk.Button(self, image = self.photo,
                                      text = movie["title"], compound = "top", bg = "gray11", 
                                      fg = "white", command = self.handle_click)
        self.image_button.grid(row = 0, column = 0, rowspan = 2, padx = (0,15), sticky ="n")

        # Add hover effect
        self.image_button.bind("<Enter>", self.on_enter)
        self.image_button.bind("<Leave>", self.on_leave)

        self.movie_titles = tk.Label(self, text = movie["title"], bg = "gray17", fg = "sienna1",
                                    font = ("Helvetica", 14, "bold"), justify = "left", anchor = "center")
        self.movie_titles.grid(row =0, column = 1, sticky = "w")

        self.movie_description = tk.Label(self, text = movie["description"], bg = "gray17", fg = "sienna1",
                                        font = ("Helvetica", 12, "italic"), justify = "left", wraplength=700, anchor = "w")
        self.movie_description.grid(row = 1, column = 1, sticky = "w")

    def handle_click(self):
        self.on_click(self.movie)

    def on_enter(self, event):
        self.image_button.config(bg="sienna1")

    def on_leave(self, event):
        self.image_button.config(bg="gray11")


class ShowtimePopup(tk.Toplevel):
    """
    Class Name: ShowtimePopup
    Date: 04-17-2026
    Programmer: Allison Berkeland

    Descripton: This class creates a popup window for customers
      to select showtimes for a chosen movie. It displays the movie 
      title, available showtimes, and allows the user to select a 
      showtime or go back to the movie selection screen.
      
      Functions:
        - _build_ui(): Constructs the UI elements for showtime selection
        - _generate_showtimes(): Returns list of available showtimes
        - _select_showtime(showtime): Stores selected hsowtime and updates UI
        - _go_back(): Returns to showtime selection screen
        - _sleect_seats(): Proceeds to seat selection

        Inputs:
        - parent: parent window
        - movie: dictionary containing movie details

        Data Structures:
         - Uses a list of strings to store showtimes
         - Stores selected showtime as a string

         Algorithms:
         - UI state update logic:
            Rebuilds the interface depending if a showtime has been selected
            or not.
    """
    def __init__(self, parent, db, user, movie):
        """
        Initializes the popup window and sets intial state.
        """
        super().__init__(parent, bg="gray12")
        self.db = db
        self.user = user
        self.movie = movie
        self.movies_service = MovieService(self.db)
        self.selected_showtime = None
        self.selected_showing = None

        self.title(f"{movie['title']} - Select Showtime")
        self.geometry("1000x850")
        self.configure(bg="gray12")
        
        # Center the popup window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (850 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.main_frame = tk.Frame(self, bg="gray12")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._build_ui()
    
    def _build_ui(self):
        """
        Builds and updates the popup UI.
        If no showtimes is selected, displays available showtimes. 
        If a showtime is selected, displays the selected showtime and 
        next steps.
        """
        # Clear previous widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Title label
        title_label = tk.Label(self.main_frame, text=f"{self.movie['title']}", 
                              bg="gray12", fg="sienna1", 
                              font=("Helvetica", 16, "bold"))
        title_label.pack(pady=15)
        
        if self.selected_showtime is None:
            # Show showtimes selection
            showtimes_label = tk.Label(self.main_frame, text="Available Showtimes:", 
                                      bg="gray12", fg="white",
                                      font=("Helvetica", 12, "bold"))
            showtimes_label.pack(anchor="w", pady=(10, 5))
            
            # Generate 5 sample showtimes
            showtimes = self._generate_showtimes()
            
            if not showtimes:
                no_showtimes = tk.Label(self.main_frame, text = "No available showtimes", 
                               bg = "gray12", fg = "white", font = ("Helvetica", 12, "bold"))
                no_showtimes.pack(pady = 10)

            else: 
            # Create buttons for each showtime
                for showtime in showtimes:
                    dtime = datetime.strptime(showtime["show_datetime"], "%Y-%m-%d %H:%M:%S")
                    btn_txt = (
                        f"{dtime.strftime('%b %d, %Y - %I:%M %p')}\n "
                        f"{showtime['theatre_name']} ({showtime['city']}) \n "
                        f"{showtime['screen_name']} | ${showtime['base_price']:.2f}"
                    )
                    btn = tk.Button(self.main_frame, text=btn_txt, 
                                bg="gray17", fg="sienna1",
                                font=("Helvetica", 11),
                                width=25,
                                command=lambda st=showtime: self._select_showtime(st))
                    btn.pack(pady=5)
                
                # Hover effect
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="sienna1", fg="gray12"))
                    btn.bind("<Leave>", lambda e, b=btn: b.config(bg="gray17", fg="sienna1"))
        else:
            # Show selected showtime and seat selection option
            selected_label = tk.Label(self.main_frame, text="Selected Showtime:", 
                                     bg="gray12", fg="white",
                                     font=("Helvetica", 12, "bold"))
            selected_label.pack(pady=(10, 5))
            
            time_display = tk.Label(self.main_frame, text=self.selected_showtime, 
                                   bg="gray17", fg="sienna1",
                                   font=("Helvetica", 14, "bold"),
                                   padx=10, pady=10)
            time_display.pack(pady=15, fill="x")
            
            # Select Seats button
            seats_btn = tk.Button(self.main_frame, text="Select Seats", 
                                 bg="sienna1", fg="gray12",
                                 font=("Helvetica", 12, "bold"),
                                 padx=20, pady=10,
                                 command=self._select_seats)
            seats_btn.pack(pady=20)
            
            # Hover effect for seats button
            seats_btn.bind("<Enter>", lambda e, b=seats_btn: b.config(bg="lightsalmon"))
            seats_btn.bind("<Leave>", lambda e, b=seats_btn: b.config(bg="sienna1"))
            
            # Go Back button
            back_btn = tk.Button(self.main_frame, text="Go Back", 
                                bg="gray17", fg="sienna1",
                                font=("Helvetica", 10),
                                command=self._go_back)
            back_btn.pack(pady=5)
            
            # Hover effect for back button
            back_btn.bind("<Enter>", lambda e, b=back_btn: b.config(bg="sienna1", fg="gray12"))
            back_btn.bind("<Leave>", lambda e, b=back_btn: b.config(bg="gray17", fg="sienna1"))
        
        # Close button (always visible)
        close_btn = tk.Button(self.main_frame, text="Close", 
                            bg="gray17", fg="white",
                            font=("Helvetica", 10),
                            command=self.destroy)
        close_btn.pack(pady=10)
    
    def _generate_showtimes(self):
        """Generate 5 sample showtimes"""
        #times = ["2:00 PM", "4:30 PM", "7:00 PM", "9:30 PM", "11:00 PM"]
        #return times
        #replaced hardcoded times with backend data
        return self.movies_service.get_shows_for_movie(self.movie["movie_id"])
    
    #connects frontend with backend (recieves showtime info/details)
    def _select_showtime(self, showtime):
        """Handle showtime selection"""
        self.selected_showing = showtime
        dtime = datetime.strptime(showtime["show_datetime"], "%Y-%m-%d %H:%M:%S")
        self.selected_showtime = (
            f"{dtime.strftime('%b %d, %Y - %I:%M %p')} | "
            f"{showtime['theatre_name']} ({showtime['city']}) | "
            f"{showtime['screen_name']} | ${showtime['base_price']:.2f}"
        )
        self._build_ui()
    
    def _go_back(self):
        """Go back to showtime selection"""
        self.selected_showtime = None
        self.selected_showing = None
        self._build_ui()
    
    #takes us to next window
    def _select_seats(self):
        """Handle seat selection"""
        from .seat_picker import SeatPicker
        self.withdraw()
        SeatPicker(self, self.db, self.user, self.movie, self.selected_showing)
    
