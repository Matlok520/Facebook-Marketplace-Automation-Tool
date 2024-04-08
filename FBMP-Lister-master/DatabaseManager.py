import sqlite3

class DatabaseManager:
    def __init__(self, dbPath='products.db'):
        self.dbPath = dbPath
        self.initializeDb()

    def initializeDb(self):
        with sqlite3.connect(self.dbPath) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                                id INTEGER PRIMARY KEY,
                                url TEXT UNIQUE,
                                title TEXT
                              )''')

    def addProduct(self, url, title):
        try:
            with sqlite3.connect(self.dbPath) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (url, title) VALUES (?, ?)", (url, title))
        except sqlite3.IntegrityError:
            print(f"Product with URL {url} already exists.")

    def productAlreadyExistsInDatabase(self, url, title):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        c.execute("SELECT 1 FROM products WHERE url=? AND title=?", (url, title))
        if c.fetchone() is None:
            conn.close()
            return False
        else:
            print("Product found in database")
            conn.close()
            return True
