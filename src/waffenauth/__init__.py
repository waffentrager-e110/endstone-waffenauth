import os
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone import Player, ColorFormat

from .database import Database
from .listener import WaffenAuthListener

class WaffenAuth(Plugin):
    # Метаданные (можно не указывать, они берутся из pyproject.toml)
    description = "Система авторизации с GUI и SQLite"
    version = "0.4.0"
    api_version = "0.11"

    # Регистрация команд через словарь (правильный способ!)
    commands = {
        "register": {
            "description": "Регистрация на сервере",
            "usages": ["/register <password>"],
            "permissions": ["waffenauth.register"]
        },
        "login": {
            "description": "Вход на сервер",
            "usages": ["/login <password>"],
            "permissions": ["waffenauth.login"]
        }
    }

    # Права (опционально)
    permissions = {
        "waffenauth.register": {
            "description": "Позволяет регистрироваться",
            "default": True
        },
        "waffenauth.login": {
            "description": "Позволяет войти",
            "default": True
        }
    }

    def on_load(self) -> None:
        """Вызывается при загрузке плагина (до on_enable)."""
        # Создаём папку для данных, если её нет
        self.data_folder = os.path.join(os.getcwd(), "plugins", "endstone_waffenauth")
        os.makedirs(self.data_folder, exist_ok=True)

        # Инициализируем базу данных
        self.db = Database(self.data_folder)

        # Создаём конфиг по умолчанию, если его нет
        self.save_default_config()

        # Множество авторизованных игроков
        self.authorized = set()

    def on_enable(self) -> None:
        """Вызывается при включении плагина."""
        self.logger.info(f"{ColorFormat.GREEN}WaffenAuth v{self.version} загружен!{ColorFormat.RESET}")

        # Регистрируем слушатели событий
        self.register_events(WaffenAuthListener(self))

        # Запускаем таймер напоминаний (каждые 40 тиков = 2 секунды)
        self.server.scheduler.run_task(self, self._reminder_tick, delay=20, period=40)

        self.logger.info("Плагин готов к работе.")

    def on_disable(self) -> None:
        """Вызывается при выключении плагина."""
        self.logger.info(f"{ColorFormat.RED}WaffenAuth выгружен.{ColorFormat.RESET}")

    def _reminder_tick(self) -> None:
        """Отправляет напоминания неавторизованным игрокам."""
        for player in self.server.online_players:
            if player.name not in self.authorized:
                player.send_message(self.get_message("reminder_title"))
                player.send_message(self.get_message("reminder_register"))
                player.send_message(self.get_message("reminder_login"))
                player.send_message(self.get_message("reminder_footer"))

    def get_message(self, key: str) -> str:
        """Возвращает сообщение из конфига или стандартное."""
        default_messages = {
            "reminder_title": f"{ColorFormat.YELLOW}========== WaffenAuth ==========",
            "reminder_register": f"{ColorFormat.GREEN}/register <password> {ColorFormat.WHITE}- Register",
            "reminder_login": f"{ColorFormat.GREEN}/login <password> {ColorFormat.WHITE}- Login",
            "reminder_footer": f"{ColorFormat.YELLOW}=================================",
            "register_success": f"{ColorFormat.GREEN}You have successfully registered!",
            "login_success": f"{ColorFormat.GREEN}You have successfully logged in!",
            "register_exists": f"{ColorFormat.RED}You are already registered!",
            "wrong_password": f"{ColorFormat.RED}Wrong password!",
            "not_registered": f"{ColorFormat.RED}You are not registered! Use /register",
            "move_blocked": f"{ColorFormat.RED}You are not authorized!",
            "command_blocked": f"{ColorFormat.RED}You must register/login first!"
        }
        # Здесь можно добавить чтение из конфига, если нужно
        return default_messages.get(key, key)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        """Обработчик команд (вызывается автоматически для зарегистрированных команд)."""
        if not isinstance(sender, Player):
            sender.send_message(f"{ColorFormat.RED}This command can only be used by players.")
            return True

        player = sender
        cmd = command.name

        if cmd == "register":
            return self._handle_register(player, args)
        elif cmd == "login":
            return self._handle_login(player, args)

        return False

    def _handle_register(self, player: Player, args: list[str]) -> bool:
        if len(args) != 1:
            player.send_message(f"{ColorFormat.RED}Usage: /register <password>")
            return True

        password = args[0]
        if len(password) < 4:
            player.send_message(f"{ColorFormat.RED}Password must be at least 4 characters.")
            return True

        if self.db.user_exists(player.name):
            player.send_message(self.get_message("register_exists"))
            return True

        if self.db.register(player.name, password):
            player.send_message(self.get_message("register_success"))
            self.logger.info(f"Player {player.name} registered.")
        else:
            player.send_message(f"{ColorFormat.RED}Registration failed.")
        return True

    def _handle_login(self, player: Player, args: list[str]) -> bool:
        if len(args) != 1:
            player.send_message(f"{ColorFormat.RED}Usage: /login <password>")
            return True

        password = args[0]
        if not self.db.user_exists(player.name):
            player.send_message(self.get_message("not_registered"))
            return True

        if self.db.check_password(player.name, password):
            self.authorized.add(player.name)
            player.send_message(self.get_message("login_success"))
            self.logger.info(f"Player {player.name} logged in.")
        else:
            player.send_message(self.get_message("wrong_password"))
        return True
