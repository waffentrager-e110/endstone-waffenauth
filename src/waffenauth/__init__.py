import os
import sqlite3
from endstone.plugin import Plugin

class WaffenAuth(Plugin):
    commands = {
        "register": {
            "description": "Register on the server",
            "usages": ["/register <password>"],
        },
        "login": {
            "description": "Login to the server",
            "usages": ["/login <password>"],
        },
    }

    def on_enable(self) -> None:
        self.logger.info("§aWaffenAuth v0.3.0 загружен!")
        
        self.data_folder = os.path.join(os.getcwd(), "plugins", "endstone_waffenauth")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        self.db_path = os.path.join(self.data_folder, "auth.db")
        self.init_database()
        
        self.auth_players = set()
        
        self.logger.info(f"  - База данных: {self.db_path}")
        
        # Запускаем напоминания
        self.server.scheduler.run_task(self, self.reminder_tick, delay=20, period=40)
        
        self.logger.info("§aПлагин готов к работе!")
    
    def on_disable(self) -> None:
        self.logger.info("§cWaffenAuth выгружен.")
    
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
    
    def reminder_tick(self) -> None:
        try:
            players = self.server.get_online_players()
            for player in players:
                if player.name not in self.auth_players:
                    player.send_message("§e========== WaffenAuth ==========")
                    player.send_message("§a/register <password> §7- Register")
                    player.send_message("§a/login <password> §7- Login")
                    player.send_message("§e=================================")
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
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
            self.logger.info(f"Player {name} registered")
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
                self.logger.info(f"Player {name} logged in")
            else:
                sender.send_message("§cWrong password!")
            
            return True
        
        return False
