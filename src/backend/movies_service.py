movies = [
    {
        "id": 1,
        "title": "Avengers: Endgame",
        "genre": "Action",
        "duration": 181,
        "showtimes": ["1:00 PM", "4:30 PM", "8:00 PM"],
        "available_seats": 45
    },
    {
        "id": 2,
        "title": "Inception",
        "genre": "Sci-Fi",
        "duration": 148,
        "showtimes": ["12:00 PM", "3:30 PM", "7:00 PM"],
        "available_seats": 30
    },
    {
        "id": 3,
        "title": "The Lion King",
        "genre": "Animation",
        "duration": 88,
        "showtimes": ["10:00 AM", "1:30 PM", "5:00 PM"],
        "available_seats": 20
    }
]


def display_all_movies():
    print("\nAvailable Movies:")
    print("-" * 50)

    for movie in movies:
        print(f"ID: {movie['id']}")
        print(f"Title: {movie['title']}")
        print(f"Genre: {movie['genre']}")
        print(f"Duration: {movie['duration']} minutes")
        print(f"Showtimes: {', '.join(movie['showtimes'])}")
        print(f"Available Seats: {movie['available_seats']}")
        print("-" * 50)


def display_movie_by_id(movie_id):
    found = False

    for movie in movies:
        if movie["id"] == movie_id:
            print("\nMovie Found:")
            print("-" * 50)
            print(f"ID: {movie['id']}")
            print(f"Title: {movie['title']}")
            print(f"Genre: {movie['genre']}")
            print(f"Duration: {movie['duration']} minutes")
            print(f"Showtimes: {', '.join(movie['showtimes'])}")
            print(f"Available Seats: {movie['available_seats']}")
            print("-" * 50)
            found = True
            break

    if not found:
        print("Movie not found.")


def main():
    while True:
        print("\nMovie Reservation System")
        print("1. View all available movies")
        print("2. View movie by ID")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_all_movies()
        elif choice == "2":
            try:
                movie_id = int(input("Enter movie ID: "))
                display_movie_by_id(movie_id)
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "3":
            print("Exiting system...")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()