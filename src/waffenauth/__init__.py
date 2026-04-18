import os
import sqlite3
from endstone.plugin import Plugin

class WaffenAuth(Plugin):
    def on_enable(self) -> None:
        self.get_logger().info("§aWaffenAuth v0.3.0 загружен!")
        
        my_data_folder = os.path.join(os.getcwd(), "plugins", "endstone_waffenauth")
        if not os.path.exists(my_data_folder):
            os.makedirs(my_data_folder)
        
        self.db_path = os.path.join(my_data_folder, "auth.db")
        self.init_database()
        
        self.auth_players = set()
        
        self.get_logger().info(f"  - База данных: {self.db_path}")
        self.get_logger().info("§aПлагин готов к работе!")
    
    def on_disable(self) -> None:
        self.get_logger().info("§cWaffenAuth выгружен.")
    
    def init_database(self) -> None:
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
    
    def on_command(self, sender, command, args):
        from endstone import Player
        
        if not isinstance(sender, Player):
            return True
        
        cmd = command.name
        
        if cmd == "register" and len(args) >= 1:
            name = sender.name
            password = args[0]
            
            if len(password) < 4:
                sender.send_message("§cPassword must be at least 4 characters")
                return True
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE name = ?", (name.lower(),))
            exists = cursor.fetchone()
            
            if exists:
                sender.send_message("§cYou are already registered!")
                conn.close()
                return True
            
            cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)",
                          (name.lower(), password))
            conn.commit()
            conn.close()
            
            sender.send_message("§aYou have successfully registered!")
            self.get_logger().info(f"Player {name} registered")
            return True
        
        elif cmd == "login" and len(args) >= 1:
            name = sender.name
            password = args[0]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                sender.send_message("§cYou are not registered! Use /register")
                return True
            
            if row[0] == password:
                self.auth_players.add(name)
                sender.send_message("§aYou have successfully logged in!")
                self.get_logger().info(f"Player {name} logged in")
            else:
                sender.send_message("§cWrong password!")
            
            return True
        
        return False
