import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image

from src.backend.database import DB

class MovieListFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg = "gray12")

        self.app = app
        
        self.configure(bg = "gray12")

        movie_list_container = tk.Frame(self, bg="gray13")
        movie_list_container.pack(expand = True, fill = "both", padx=40, pady=40)

        self.canvas = tk.Canvas(movie_list_container, bg = "gray13")
        self.canvas.pack(side = "left", fill = "both", expand = True)
        scrollbar = tk.Scrollbar(movie_list_container, orient = "vertical",
                         command = self.canvas.yview)
        scrollbar.pack(side = "right", fill = "y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas, bg="gray12")
        self.canvas_window = self.canvas.create_window((0,0), 
                                    window = self.scrollable_frame, anchor = "nw")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.new_scroll_frame)


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

        for movie in movies:
            card = MovieCard(self.scrollable_frame, movie, on_click = self.select_movie)
            card.pack(fill="x", padx=10, pady=10)

    def new_scroll_frame(self,event):
            self.canvas.itemconfig(self.canvas_window, width = event.width)

    def select_movie(self, movie):
        print("selected:", movie["title"])


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

        self.movie_titles = tk.Label(self, text = movie["title"], bg = "gray17", fg = "sienna1",
                            font = ("Helvetica", 14, "bold"), justify = "left", anchor = "center")
        self.movie_titles.grid(row =0, column = 1, sticky = "w")

        self.movie_description = tk.Label(self, text = movie["description"], bg = "gray17", fg = "sienna1",
                                font = ("Helvetica", 12, "italic"), justify = "left", wraplength=700, anchor = "w")
        self.movie_description.grid(row = 1, column = 1, sticky = "w")

    def handle_click(self):
        self.on_click(self.movie)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Movie List")
    root.geometry("1000x900")

    test_frame = MovieListFrame(root, app=None)
    test_frame.pack(fill = "both", expand = True)

    root.mainloop()

    