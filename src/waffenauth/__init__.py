from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from .auth_manager import AuthManager
from .gui_manager import GUIManager

class WaffenAuth(Plugin):
    """Плагин авторизации с GUI"""
    
    def on_enable(self) -> None:
        self.logger.info("§a=====================================")
        self.logger.info("§e   WaffenAuth v0.1.0 загружен!")
        self.logger.info("§a=====================================")
        
        # Инициализация менеджеров
        self.auth_manager = AuthManager(self)
        self.gui_manager = GUIManager(self)
        
        self.logger.info("  - Система авторизации готова")
        self.logger.info("  - GUI формы готовы")
    
    def on_disable(self) -> None:
        self.logger.info("§cWaffenAuth выгружен.")
    
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name == "register" and len(args) >= 1:
            return self.auth_manager.register(sender, args[0])
        elif command.name == "login" and len(args) >= 1:
            return self.auth_manager.login(sender, args[0])
        return False
