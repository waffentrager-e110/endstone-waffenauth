from time import time
from endstone import ColorFormat
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin
from typing_extensions import override

from endstone_waffenauth.database import check_password, initialize_database, register_user, user_exists
from endstone_waffenauth.listener import WaffenAuthListener

class WaffenAuth(Plugin):
    description = "WaffenAuth - система авторизации"
    version = "0.3.0"
    api_version = "0.11"
    authors = ["Waffentrager"]

    def __init__(self) -> None:
        super().__init__()
        self.auth_players: set[str] = set()
        self.db_path: str | None = None

    commands = {
        "register": {
            "description": "Регистрация на сервере",
            "usages": ["/register <пароль>"],
            "permissions": ["waffenauth.register"],
        },
        "login": {
            "description": "Вход на сервер",
            "usages": ["/login <пароль>"],
            "permissions": ["waffenauth.login"],
        },
    }

    permissions = {
        "waffenauth.register": {
            "description": "Позволяет регистрироваться",
            "default": True,
        },
        "waffenauth.login": {
            "description": "Позволяет войти",
            "default": True,
        },
    }

    @override
    def on_load(self) -> None:
        """Вызывается при загрузке плагина"""
        self.db_path = initialize_database(self.data_folder)
        self.logger.info(f"WaffenAuth is loading... (v{self.version})")

    @override
    def on_enable(self) -> None:
        """Вызывается при включении плагина"""
        self.save_default_config()
        self.register_events(WaffenAuthListener(self))
        
        # Запускаем напоминания (каждые 2 секунды = 40 тиков)
        self.server.scheduler.run_task(self, self._reminder_tick, delay=20, period=40)
        
        self.logger.info(f"WaffenAuth has been enabled! (v{self.version})")

    @override
    def on_disable(self) -> None:
        """Вызывается при выключении плагина"""
        self.logger.info(f"WaffenAuth has been disabled! (v{self.version})")

    def get_message(self, key: str) -> str:
        """Возвращает сообщение из конфига"""
        messages = self.config.get("messages", {})
        default_messages = {
            "register_success": "§aВы успешно зарегистрированы!",
            "login_success": "§aВы успешно вошли на сервер!",
            "register_exists": "§cВы уже зарегистрированы!",
            "wrong_password": "§cНеверный пароль!",
            "not_registered": "§cВы не зарегистрированы!",
            "move_blocked": "§cВы не авторизованы!",
            "command_blocked": "§cСначала авторизуйтесь! Используйте /register или /login",
            "reminder_title": "§e========== WaffenAuth ==========",
            "reminder_register": "§a/register <пароль> §7- Регистрация",
            "reminder_login": "§a/login <пароль> §7- Вход",
            "reminder_footer": "§e=================================",
        }
        return messages.get(key, default_messages.get(key, key))

    def _reminder_tick(self) -> None:
        """Отправляет напоминания неавторизованным игрокам"""
        for player in self.server.get_online_players():
            if player.name not in self.auth_players:
                player.send_message(self.get_message("reminder_title"))
                player.send_message(self.get_message("reminder_register"))
                player.send_message(self.get_message("reminder_login"))
                player.send_message(self.get_message("reminder_footer"))

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        from endstone import Player
        
        if not isinstance(sender, Player):
            sender.send_message(f"{ColorFormat.RED}Only players can use this command.")
            return True

        match command.name:
            case "register":
                return self._handle_register(sender, args)
            case "login":
                return self._handle_login(sender, args)
        return False

    def _handle_register(self, player: Player, args: list[str]) -> bool:
        if len(args) != 1:
            player.send_message(f"{ColorFormat.RED}Usage: /register <password>")
            return True

        password = args[0]
        name = player.name

        if len(password) < 4:
            player.send_message(f"{ColorFormat.RED}Password must be at least 4 characters.")
            return True

        if user_exists(str(self.db_path), name):
            player.send_message(self.get_message("register_exists"))
            return True

        if register_user(str(self.db_path), name, password):
            player.send_message(self.get_message("register_success"))
            self.logger.info(f"Player {name} registered")
        else:
            player.send_message(f"{ColorFormat.RED}Registration failed.")
        
        return True

    def _handle_login(self, player: Player, args: list[str]) -> bool:
        if len(args) != 1:
            player.send_message(f"{ColorFormat.RED}Usage: /login <password>")
            return True

        password = args[0]
        name = player.name

        if not user_exists(str(self.db_path), name):
            player.send_message(self.get_message("not_registered"))
            return True

        if check_password(str(self.db_path), name, password):
            self.auth_players.add(name)
            player.send_message(self.get_message("login_success"))
            self.logger.info(f"Player {name} logged in")
        else:
            player.send_message(self.get_message("wrong_password"))
        
        return True
