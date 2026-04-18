from endstone.plugin import Plugin

class WaffenAuth(Plugin):
    def on_enable(self) -> None:
        self.logger.info("§aWaffenAuth v0.1.0 загружен!")

    def on_disable(self) -> None:
        self.logger.info("§cWaffenAuth выгружен.")
