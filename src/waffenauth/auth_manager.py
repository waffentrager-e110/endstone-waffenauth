from endstone import Player
from endstone.plugin import Plugin
from .database import Database

class AuthManager:
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.db = None
        self.logged_in = set()
        self.timeout_tasks = {}
    
    def init_database(self) -> None:
        """Инициализирует базу данных"""
        db_file = self.plugin.config.get('database.file', 'WaffenAuth/auth.db')
        self.db = Database(db_file)
    
    def register(self, player: Player, password: str) -> bool:
        """Регистрирует игрока"""
        name = player.name
        
        if self.db.user_exists(name):
            player.send_message(self.plugin.config.get('messages.register_exists'))
            return False
        
        if len(password) < 4:
            player.send_message("§cПароль должен быть не менее 4 символов")
            return False
        
        if self.db.register_user(name, password):
            player.send_message(self.plugin.config.get('messages.register_success'))
            return True
        
        player.send_message("§cОшибка при регистрации")
        return False
    
    def login(self, player: Player, password: str) -> bool:
        """Авторизует игрока"""
        name = player.name
        
        if not self.db.user_exists(name):
            player.send_message(self.plugin.config.get('messages.not_registered'))
            return False
        
        if self.db.check_password(name, password):
            self.logged_in.add(name)
            player.send_message(self.plugin.config.get('messages.login_success'))
            self.cancel_timeout(player)
            return True
        
        player.send_message(self.plugin.config.get('messages.wrong_password'))
        return False
    
    def is_logged_in(self, player: Player) -> bool:
        """Проверяет авторизован ли игрок"""
        return player.name in self.logged_in
    
    def start_timeout(self, player: Player) -> None:
        """Запускает таймер на отключение"""
        timeout = self.plugin.config.get('timeout', 30)
        
        async def kick_task():
            import asyncio
            await asyncio.sleep(timeout)
            if not self.is_logged_in(player):
                player.kick(f"§cВремя авторизации истекло ({timeout} сек.)")
        
        import asyncio
        task = asyncio.create_task(kick_task())
        self.timeout_tasks[player.name] = task
    
    def cancel_timeout(self, player: Player) -> None:
        """Отменяет таймер отключения"""
        if player.name in self.timeout_tasks:
            self.timeout_tasks[player.name].cancel()
            del self.timeout_tasks[player.name]
    
    def logout(self, player: Player) -> None:
        """Выход игрока"""
        self.logged_in.discard(player.name)
