from endstone import Player
from endstone.plugin import Plugin
import json
import os

class AuthManager:
    """Менеджер авторизации"""
    
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.players: dict[str, str] = {}  # Имя -> пароль
        self.logged_in: set[str] = set()   # Авторизованные игроки
        self.data_file = "auth_data.json"
        self._load_data()
    
    def _load_data(self) -> None:
        """Загружает данные из файла"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.players = json.load(f)
    
    def _save_data(self) -> None:
        """Сохраняет данные в файл"""
        with open(self.data_file, 'w') as f:
            json.dump(self.players, f)
    
    def register(self, player: Player, password: str) -> bool:
        """Регистрация игрока"""
        name = player.name
        
        if name in self.players:
            player.send_message("§cВы уже зарегистрированы! Используйте /login")
            return False
        
        if len(password) < 4:
            player.send_message("§cПароль должен быть не менее 4 символов")
            return False
        
        self.players[name] = password
        self._save_data()
        player.send_message("§aРегистрация успешна! Теперь войдите: /login [пароль]")
        return True
    
    def login(self, player: Player, password: str) -> bool:
        """Вход игрока"""
        name = player.name
        
        if name not in self.players:
            player.send_message("§cВы не зарегистрированы! Используйте /register [пароль]")
            return False
        
        if self.players[name] != password:
            player.send_message("§cНеверный пароль!")
            return False
        
        self.logged_in.add(name)
        player.send_message("§aВы успешно вошли на сервер!")
        return True
    
    def is_logged_in(self, player: Player) -> bool:
        """Проверяет, авторизован ли игрок"""
        return player.name in self.logged_in
    
    def logout(self, player: Player) -> None:
        """Выход игрока"""
        self.logged_in.discard(player.name)
