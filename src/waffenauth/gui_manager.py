from endstone import Player
from endstone.plugin import Plugin

class GUIManager:
    """Менеджер GUI форм"""
    
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
    
    def show_auth_form(self, player: Player) -> None:
        """Показывает форму авторизации"""
        # В Endstone GUI пока через команды
        # Полноценный GUI появится в следующих версиях
        player.send_message("§e========== WaffenAuth ==========")
        player.send_message("§a/register [пароль] §7- Регистрация")
        player.send_message("§a/login [пароль] §7- Вход")
        player.send_message("§e=================================")
