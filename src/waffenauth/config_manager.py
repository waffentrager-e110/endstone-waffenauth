import os
import tomllib
from endstone.plugin import Plugin

class ConfigManager:
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.config_dir = "WaffenAuth"
        self.config_file = f"{self.config_dir}/config.toml"
        self.data = {}
    
    def load(self) -> None:
        """Загружает конфигурацию"""
        # Создаём папку если нет
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Создаём конфиг если нет
        if not os.path.exists(self.config_file):
            self.create_default_config()
        
        # Загружаем конфиг
        with open(self.config_file, "rb") as f:
            self.data = tomllib.load(f)
    
    def create_default_config(self) -> None:
        """Создаёт конфиг по умолчанию"""
        default_config = '''# WaffenAuth Configuration

# Время на авторизацию в секундах (timeout)
timeout = 30

# Настройки базы данных
[database]
type = "sqlite"
file = "WaffenAuth/auth.db"

# Сообщения
[messages]
register_success = "§aВы успешно зарегистрированы!"
login_success = "§aВы успешно вошли на сервер!"
register_exists = "§cИгрок с таким ником уже зарегистрирован!"
wrong_password = "§cНеверный пароль!"
not_registered = "§cВы не зарегистрированы! Используйте /register"
already_logged = "§cВы уже авторизованы!"
move_blocked = "§cВы не авторизованы! Используйте /register или /login"
reminder_title = "§e========== WaffenAuth =========="
reminder_register = "§a/register <пароль> §7- Регистрация"
reminder_login = "§a/login <пароль> §7- Вход"
reminder_footer = "§e================================="
'''
        with open(self.config_file, "w") as f:
            f.write(default_config)
    
    def get(self, key: str, default=None):
        """Получает значение из конфига"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
