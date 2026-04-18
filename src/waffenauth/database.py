import sqlite3
from pathlib import Path

def initialize_database(data_folder: str | Path):
    """Инициализирует базу данных"""
    database_folder = Path(data_folder)
    database_folder.mkdir(parents=True, exist_ok=True)
    
    db_path = database_folder / "auth.db"
    conn = sqlite3.connect(db_path)
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
    return db_path

def register_user(db_path: str, name: str, password: str) -> bool:
    """Регистрирует пользователя"""
    conn = sqlite3.connect(db_path)
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

def check_password(db_path: str, name: str, password: str) -> bool:
    """Проверяет пароль"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE name = ?", (name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row is not None and row[0] == password

def user_exists(db_path: str, name: str) -> bool:
    """Проверяет существование пользователя"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE name = ?", (name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row is not None
