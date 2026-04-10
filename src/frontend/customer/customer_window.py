import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from datetime import datetime, timedelta

from src.backend.database import DB

class CustomerWindow(tk.Frame):
    def __init__(self, master, db, user):
        super().__init__(master, bg = "gray12")

        self.db =db
        self.user = user
        self.master.eval('tk::PlaceWindow . center')
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
        self.configure(bg = "gray12")

        movie_list_container = tk.Frame(self, bg=  "gray13")
        movie_list_container.pack(expand = True, fill = "both", padx=40, pady=40)

        self.canvas = tk.Canvas(movie_list_container, bg = "gray13")
        self.canvas.pack(side = "left", fill = "both", expand = True)

        scrollbar = tk.Scrollbar(movie_list_container, orient = "vertical",
                                 command = self.canvas.yview)
        scrollbar.pack(side = "right", fill = "y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas, bg="gray12")
        self.canvas_window = self.canvas.create_window((0,0), window = self.scrollable_frame, anchor = "nw")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.new_scroll_frame)

        #Just inbuilt, adjustable as necessary
        movies = [
                {"title": "Interstellar",
                "image": "assets/movieposters/Interstellar.png",
                "description": ("In a future where Earth is becoming uninhabitable, a former pilot "
                "(Matthew McConaughey) joins a mission to travel beyond our galaxy in search of a new"
                " home for humanity. As the journey pushes the limits of time and space, the crew must"
                " confront impossible choices and the true cost of survival.")
                },
                {"title": "Arrival",
                "image": "assets/movieposters/Arrival.png",
                "description": ("When mysterious spacecraft appear around the world, a linguist (Amy Adams)"
                " is recruited to communicate with the unknown visitors. As she works to understand their language,"
                " the line between past, present, and future begins to blur.")
                },
                {"title": "Hacksaw Ridge",
                "image": "assets/movieposters/HacksawRidge.png", 
                "description":("Desmond Doss (Andrew Garfield), a deeply religious young man, enlists in"
                " the U.S. Army during World War II but refuses to carry a weapon. As he faces intense "
                "skepticism from fellow soldiers and superiors, his beliefs are put to the ultimate test"
                " when he’s sent into one of the war’s deadliest battles.")
                },
                {"title": "Across the Spiderverse",
                "image": "assets/movieposters/AcrossTheSpiderverse.png",
                "description": ("Miles Morales reunites with Gwen Stacy and is pulled into a vast multiverse of "
                "Spider-People. When he encounters a powerful new threat, Miles must redefine what it means to be a hero.")
                }, 
                {"title" : "The Maze Runner",
                "image": "assets/movieposters/TheMazeRunner.png",
                "description":("A teenage boy (Dylan O’Brien) wakes up in a mysterious glade surrounded by a massive,"
                " ever-changing maze with no memory of his past. As he adapts to life among the other boys trapped there,"
                " he becomes determined to uncover the maze’s secrets and find a way out.")
                },
                {"title" : "Howl's Moving Castle",
                "image": "assets/movieposters/HowlsMovingCastle.png",
                "description":("A young woman named Sophie is mysteriously transformed into"
                " an old woman and seeks refuge in the magical moving castle of the wizard Howl."
                " As she navigates a world of war and enchantment, she discovers that nothing "
                "is quite what it seems.")
                }
            ]
        #creates a movie card/slot in our layout for each movie
        for movie in movies:
            card = MovieCard(self.scrollable_frame, movie, on_click = self.select_movie)
            card.pack(fill="x", padx=10, pady=10)

    def new_scroll_frame(self,event):
        self.canvas.itemconfig(self.canvas_window, width = event.width)

    #to ensure our button/movie can be selected
    def select_movie(self, movie):
        print("selected:", movie["title"])
        ShowtimePopup(self.master, movie)

#creates various cards using images/title (they're buttons that can be clicked on)
class MovieCard(tk.Frame):
    def __init__(self, parent, movie, on_click):
        super().__init__(parent, bg = "gray17", padx = 10, pady = 10)
         
        self.movie = movie
        self.on_click = on_click
        im = Image.open(movie["image"])
        im = im.resize((100, 140))
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
    def __init__(self, parent, movie):
        super().__init__(parent, bg="gray12")
        self.movie = movie
        self.selected_showtime = None
        self.title(f"{movie['title']} - Select Showtime")
        self.geometry("400x350")
        self.configure(bg="gray12")
        
        # Center the popup window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.main_frame = tk.Frame(self, bg="gray12")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._build_ui()
    
    def _build_ui(self):
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
            
            # Create buttons for each showtime
            for showtime in showtimes:
                btn = tk.Button(self.main_frame, text=showtime, 
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
        times = ["2:00 PM", "4:30 PM", "7:00 PM", "9:30 PM", "11:00 PM"]
        return times
    
    def _select_showtime(self, showtime):
        """Handle showtime selection"""
        self.selected_showtime = showtime
        self._build_ui()
    
    def _go_back(self):
        """Go back to showtime selection"""
        self.selected_showtime = None
        self._build_ui()
    
    def _select_seats(self):
        """Handle seat selection"""
        messagebox.showinfo("Seats", 
                          f"Proceeding to seat selection for {self.movie['title']} at {self.selected_showtime}")
        self.destroy()
    