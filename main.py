import sys
from src.backend.database import DB, init_db
from src.frontend import App

DB_PATH = "movies.db"

def main():
    db = DB(DB_PATH)
    init_db(db)

    app = App(db)
    app.mainloop()

    db.close()

if __name__ == "__main__":
    main()