import sqlite3
import logging
from pathlib import Path
from passlib.context import CryptContext

# Настройка контекста для Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL
                    )
                ''')
                # Таблица для отслеживания неудачных попыток (по имени игрока)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS failed_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logging.info(f"[WaffenAuth] Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"[WaffenAuth] Error initializing database: {e}")

    def user_exists(self, username: str) -> bool:
        """Check if a user exists in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"[WaffenAuth] Error checking if user exists: {e}")
            return False

    def get_password_hash(self, username: str) -> str | None:        """Get the password hash for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            logging.error(f"[WaffenAuth] Error getting password hash: {e}")
            return None

    def add_user(self, username: str, password: str) -> bool:
        """Hash the password and add a new user to the database."""
        try:
            password_hash = pwd_context.hash(password)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
                conn.commit()
                logging.info(f"[WaffenAuth] New user registered: {username}")
                return True
        except sqlite3.IntegrityError:
            # Username already exists
            logging.warning(f"[WaffenAuth] Attempt to register existing user: {username}")
            return False
        except Exception as e: # Catch potential hashing errors
            logging.error(f"[WaffenAuth] Error hashing password or adding user: {e}")
            return False

    def verify_password(self, username: str, password: str) -> bool:
        """Verify a password against the stored hash."""
        stored_hash = self.get_password_hash(username)
        if stored_hash:
            return pwd_context.verify(password, stored_hash)
        return False

    def log_failed_attempt(self, username: str):
        """Log a failed login attempt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO failed_attempts (username) VALUES (?)", (username,))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"[WaffenAuth] Error logging failed attempt: {e}")

    def get_failed_attempts_count(self, username: str, minutes: int = 5) -> int:
        """Get the number of failed attempts in the last N minutes."""
        try:
            with sqlite3.connect(self.db_path) as conn:                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM failed_attempts
                    WHERE username = ? AND attempt_time > datetime('now', '-{} minutes')
                """.format(minutes))
                count = cursor.fetchone()[0]
                return count
        except sqlite3.Error as e:
            logging.error(f"[WaffenAuth] Error getting failed attempts count: {e}")
            return 0

    def clear_failed_attempts(self, username: str):
        """Clear failed attempts for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM failed_attempts WHERE username = ?", (username,))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"[WaffenAuth] Error clearing failed attempts: {e}")
