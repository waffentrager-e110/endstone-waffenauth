from endstone.plugin import Plugin
from endstone.event import event_handler
from endstone.events.player import PlayerMoveEvent, PlayerCommandPreprocessEvent
from .auth_manager import AuthManager
from .config_manager import ConfigManager

class WaffenAuth(Plugin):
    def on_enable(self) -> None:
        self.logger.info("§aWaffenAuth v0.2.0 загружен!")
        
        # Загружаем конфиг
        self.config = ConfigManager(self)
        self.config.load()
        
        # Инициализируем менеджер авторизации
        self.auth_manager = AuthManager(self)
        self.auth_manager.init_database()
        
        self.logger.info(f"  - SQLite база данных готова")
        self.logger.info(f"  - Time-out: {self.config.get('timeout', 30)} сек.")
        
        # Запускаем таймер для напоминаний
        self.timer_task = None
        self.start_reminder_timer()
    
    def on_disable(self) -> None:
        if self.timer_task:
            self.timer_task.cancel()
        self.logger.info("§cWaffenAuth выгружен.")
    
    def start_reminder_timer(self) -> None:
        """Запускает таймер для отправки напоминаний"""
        import asyncio
        async def reminder_loop():
            while True:
                await asyncio.sleep(2)
                for player in self.get_server().get_online_players():
                    if not self.auth_manager.is_logged_in(player):
                        player.send_message("§e========== WaffenAuth ==========")
                        player.send_message("§a/register <пароль> §7- Регистрация")
                        player.send_message("§a/login <пароль> §7- Вход")
                        player.send_message("§e=================================")
        
        self.timer_task = asyncio.create_task(reminder_loop())
    
    @event_handler
    def on_player_move(self, event: PlayerMoveEvent) -> None:
        """Блокирует движение неавторизованных игроков"""
        player = event.get_player()
        if not self.auth_manager.is_logged_in(player):
            event.cancel()
            player.send_message("§cВы не авторизованы! Используйте /register или /login")
    
    @event_handler
    def on_player_command(self, event: PlayerCommandPreprocessEvent) -> None:
        """Разрешает только команды /register и /login неавторизованным"""
        player = event.get_player()
        if self.auth_manager.is_logged_in(player):
            return
        
        cmd = event.get_message().split()[0].lower()
        if cmd not in ["/register", "/login"]:
            event.cancel()
            player.send_message("§cСначала авторизуйтесь! Используйте /register или /login")
