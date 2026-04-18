from typing import TYPE_CHECKING
from endstone.event import event_handler
from endstone.events.player import PlayerMoveEvent, PlayerCommandPreprocessEvent

if TYPE_CHECKING:
    from endstone_waffenauth import WaffenAuth

class WaffenAuthListener:
    def __init__(self, plugin: "WaffenAuth"):
        self.plugin = plugin

    @event_handler
    def on_player_move(self, event: PlayerMoveEvent):
        player = event.player
        if player.name not in self.plugin.authorized:
            event.cancel()
            player.send_message(self.plugin.get_message("move_blocked"))

    @event_handler
    def on_player_command(self, event: PlayerCommandPreprocessEvent):
        player = event.player
        if player.name in self.plugin.authorized:
            return
        cmd = event.message.split()[0].lower()
        if cmd not in ["/register", "/login"]:
            event.cancel()
            player.send_message(self.plugin.get_message("command_blocked"))
