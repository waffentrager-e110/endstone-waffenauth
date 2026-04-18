import sqlite3
import os

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self) -> None:
        """Создаёт таблицу если нет"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                name TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def register_user(self, name: str, password: str) -> bool:
        """Регистрирует нового пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, password) VALUES (?, ?)",
                (name.lower(), password)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def check_password(self, name: str, password: str) -> bool:
        """Проверяет пароль пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE name = ?",
            (name.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == password:
            return True
        return False
    
    def user_exists(self, name: str) -> bool:
        """Проверяет существует ли пользователь"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE name = ?", (name.lower(),))
        result = cursor.fetchone()
        conn.close()
        return result is not None
