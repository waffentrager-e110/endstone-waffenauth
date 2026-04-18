import sqlite3
import os

class Database:
    def __init__(self, data_folder: str):
        self.db_path = os.path.join(data_folder, "auth.db")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                name TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def register(self, name: str, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)",
                          (name.lower(), password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def check_password(self, name: str, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE name = ?", (name.lower(),))
        row = cursor.fetchone()
        conn.close()
        return row is not None and row[0] == password

    def user_exists(self, name: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE name = ?", (name.lower(),))
        row = cursor.fetchone()
        conn.close()
        return row is not None
