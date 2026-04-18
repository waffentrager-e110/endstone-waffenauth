from endstone.plugin import Plugin
from endstone.event import PlayerJoinEvent
from endstone import ColorFormat
from database import DatabaseManager
from forms import show_login_form, show_register_form
import logging

class WaffenAuthPlugin(Plugin):
    def on_enable(self):
        # Initialize database
        self.database = DatabaseManager("waffenauth.db")
        
        # Define config values
        self.max_attempts = 5 # Maximum failed attempts before kick
        self.auth_timeout_seconds = 30 # Time before auto-kick if not authenticated

        # Register event listener
        self.server.event_manager.register_events(AuthListener(self), self)

        logging.info(f"[WaffenAuth] Version {self.description.version} is enabled!")

    def on_disable(self):
        logging.info("[WaffenAuth] is disabled!")


class AuthListener:
    def __init__(self, plugin: WaffenAuthPlugin):
        self.plugin = plugin

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        player = event.player
        
        # Check if player has the required permission
        if player.has_permission("wt.login"):
            # Player is already authenticated
            logging.info(f"[WaffenAuth] Authenticated player {player.name} joined.")
            return # Allow join

        # Player is not authenticated, start auth process
        username = player.name
        if self.plugin.database.user_exists(username):
            # Existing user needs to log in
            player.send_message("§ePlease log in to continue.")
            show_login_form(player, self.plugin)
        else:
            # New user needs to register
            player.send_message("§eWelcome new player! Please register to play.")
            show_register_form(player, self.plugin)

        # Optionally, schedule a timeout task to kick unauthenticated players
        # server.scheduler.run_taskLater(self.plugin, lambda p=player: self.timeout_check(p), self.plugin.auth_timeout_seconds * 20) # 20 ticks per second

    # Optional timeout check logic (uncomment scheduling above to use)
    # def timeout_check(self, player):
    #     if not player.has_permission("wt.login"):
    #         player.kick("Authentication timeout. Please reconnect and log in.")
    #         logging.info(f"[WaffenAuth] Kicked {player.name} due to authentication timeout.")
