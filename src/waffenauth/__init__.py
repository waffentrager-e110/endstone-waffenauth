import asyncio
import os
import sqlite3
from endstone.plugin import Plugin

class WaffenAuth(Plugin):
    def on_enable(self) -> None:
        self.logger.info("§aWaffenAuth v0.3.0 загружен!")
        
        self.data_folder = os.path.join(os.getcwd(), "plugins", "endstone_waffenauth")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        self.config = self.load_config()
        
        self.db_path = os.path.join(self.data_folder, "auth.db")
        self.init_database()
        
        self.auth_players = set()
        
        self.logger.info(f"  - База данных: {self.db_path}")
        
        self.reminder_task = asyncio.create_task(self.reminder_loop())
        
        self.logger.info("§aПлагин готов к работе!")
    
    def on_disable(self) -> None:
        if hasattr(self, 'reminder_task') and self.reminder_task:
            self.reminder_task.cancel()
        self.logger.info("§cWaffenAuth выгружен.")
    
    def load_config(self) -> dict:
        config_file = os.path.join(self.data_folder, "config.toml")
        
        default_config = {
            "timeout": 30,
            "messages": {
                "register_success": "§aВы успешно зарегистрированы!",
                "login_success": "§aВы успешно вошли на сервер!",
                "register_exists": "§cВы уже зарегистрированы!",
                "wrong_password": "§cНеверный пароль!",
                "not_registered": "§cВы не зарегистрированы!",
                "reminder_title": "§e========== WaffenAuth ==========",
                "reminder_register": "§a/register <пароль> §7- Регистрация",
                "reminder_login": "§a/login <пароль> §7- Вход",
                "reminder_footer": "§e================================="
            }
        }
        
        if not os.path.exists(config_file):
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(f"timeout = {default_config['timeout']}\n\n")
                f.write("[messages]\n")
                for k, v in default_config["messages"].items():
                    f.write(f'{k} = "{v}"\n')
            return default_config
        
        import tomllib
        with open(config_file, "rb") as f:
            return tomllib.load(f)
    
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
    
    async def reminder_loop(self) -> None:
        while True:
            await asyncio.sleep(2)
            try:
                players = self.get_server().get_online_players()
                msgs = self.config.get("messages", {})
                for player in players:
                    if player.name not in self.auth_players:
                        player.send_message(msgs.get("reminder_title", "§e========== WaffenAuth =========="))
                        player.send_message(msgs.get("reminder_register", "§a/register <пароль> §7- Регистрация"))
                        player.send_message(msgs.get("reminder_login", "§a/login <пароль> §7- Вход"))
                        player.send_message(msgs.get("reminder_footer", "§e================================="))
            except Exception as e:
                self.logger.error(f"Ошибка: {e}")
    
    def on_command(self, sender, command, args):
        from endstone import Player
        
        if not isinstance(sender, Player):
            return True
        
        cmd = command.name
        msgs = self.config.get("messages", {})
        
        if cmd == "register" and len(args) >= 1:
            name = sender.name
            password = args[0]
            
            if len(password) < 4:
                sender.send_message("§cПароль должен быть не менее 4 символов")
                return True
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE name = ?", (name.lower(),))
            exists = cursor.fetchone()
            
            if exists:
                sender.send_message(msgs.get("register_exists", "§cУже зарегистрирован!"))
                conn.close()
                return True
            
            cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)",
                          (name.lower(), password))
            conn.commit()
            conn.close()
            
            sender.send_message(msgs.get("register_success", "§aРегистрация успешна!"))
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
                sender.send_message(msgs.get("not_registered", "§cНе зарегистрирован!"))
                return True
            
            if row[0] == password:
                self.auth_players.add(name)
                sender.send_message(msgs.get("login_success", "§aВход выполнен!"))
                self.logger.info(f"{name} авторизовался")
            else:
                sender.send_message(msgs.get("wrong_password", "§cНеверный пароль!"))
            
            return True
        
        return False
