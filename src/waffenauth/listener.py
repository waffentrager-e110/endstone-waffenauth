from typing import TYPE_CHECKING
from endstone.event import PlayerCommandPreprocessEvent, PlayerMoveEvent, event_handler

if TYPE_CHECKING:
    from endstone_waffenauth import WaffenAuth

class WaffenAuthListener:
    def __init__(self, plugin: "WaffenAuth") -> None:
        self._plugin = plugin

    @event_handler
    def on_player_move(self, event: PlayerMoveEvent) -> None:
        """Блокирует движение неавторизованных игроков"""
        player = event.player
        if player.name not in self._plugin.auth_players:
            event.cancel()
            player.send_message(self._plugin.get_message("move_blocked"))

    @event_handler
    def on_player_command(self, event: PlayerCommandPreprocessEvent) -> None:
        """Разрешает только /register и /login неавторизованным"""
        player = event.player
        if player.name in self._plugin.auth_players:
            return
        
        cmd = event.message.split()[0].lower()
        if cmd not in ["/register", "/login"]:
            event.cancel()
            player.send_message(self._plugin.get_message("command_blocked"))
