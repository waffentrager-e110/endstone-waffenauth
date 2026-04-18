import asyncio
import os
import sqlite3
from endstone.plugin import Plugin

class WaffenAuth(Plugin):
    def on_enable(self) -> None:
        self.logger.info("§aWaffenAuth v0.3.0 загружен!")
        
        # Создаём папку
        self.data_folder = "WaffenAuth"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        # Загружаем конфиг
        self.config = self.load_config()
        
        # Инициализируем БД
        self.db_path = f"{self.data_folder}/auth.db"
        self.init_database()
        
        # Хранилище авторизованных
        self.logged_in = set()
        
        self.logger.info(f"  - Time-out: {self.config.get('timeout', 30)} сек.")
        
        # Запускаем напоминания
        self.reminder_task = asyncio.create_task(self.reminder_loop())
        
        # Регистрируем команды
        self.register_commands()
    
    def on_disable(self) -> None:
        if hasattr(self, 'reminder_task') and self.reminder_task:
            self.reminder_task.cancel()
        self.logger.info("§cWaffenAuth выгружен.")
    
    def load_config(self) -> dict:
        """Загружает или создаёт конфиг"""
        config_file = f"{self.data_folder}/config.toml"
        default_config = {
            "timeout": 30,
            "messages": {
                "register_success": "§aВы успешно зарегистрированы!",
                "login_success": "§aВы успешно вошли на сервер!",
                "register_exists": "§cВы уже зарегистрированы!",
                "wrong_password": "§cНеверный пароль!",
                "not_registered": "§cВы не зарегистрированы!",
                "move_blocked": "§cВы не авторизованы!",
                "reminder_title": "§e========== WaffenAuth ==========",
                "reminder_register": "§a/register <пароль> §7- Регистрация",
                "reminder_login": "§a/login <пароль> §7- Вход",
                "reminder_footer": "§e================================="
            }
        }
        
        if not os.path.exists(config_file):
            import tomli_w
            with open(config_file, "wb") as f:
                tomli_w.dump(default_config, f)
            return default_config
        
        import tomllib
        with open(config_file, "rb") as f:
            return tomllib.load(f)
    
    def init_database(self) -> None:
        """Инициализирует SQLite базу данных"""
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
    
    def register_commands(self) -> None:
        """Регистрирует команды через менеджер команд"""
        # В Endstone команды регистрируются через plugin.yml,
        # но пока сделаем через обработку сообщений в on_command
        pass
    
    async def reminder_loop(self) -> None:
        """Отправляет напоминания каждые 2 секунды"""
        while True:
            await asyncio.sleep(2)
            try:
                players = self.get_server().get_online_players()
                for player in players:
                    if player.name not in self.logged_in:
                        msg = self.config["messages"]
                        player.send_message(msg["reminder_title"])
                        player.send_message(msg["reminder_register"])
                        player.send_message(msg["reminder_login"])
                        player.send_message(msg["reminder_footer"])
            except Exception as e:
                self.logger.error(f"Ошибка в reminder_loop: {e}")
    
    def on_command(self, sender, command, args):
        """Обработка команд"""
        from endstone import Player
        
        if not isinstance(sender, Player):
            sender.send_message("§cЭта команда только для игроков.")
            return True
        
        cmd = command.name
        msgs = self.config["messages"]
        
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
                sender.send_message(msgs["register_exists"])
                conn.close()
                return True
            
            cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)",
                          (name.lower(), password))
            conn.commit()
            conn.close()
            
            sender.send_message(msgs["register_success"])
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
                sender.send_message(msgs["not_registered"])
                return True
            
            if row[0] == password:
                self.logged_in.add(name)
                sender.send_message(msgs["login_success"])
                
                # Запускаем таймер отключения через 30 секунд? Нет, снимаем блокировку
                self.logger.info(f"Игрок {name} авторизовался")
            else:
                sender.send_message(msgs["wrong_password"])
            
            return True
        
        return False
