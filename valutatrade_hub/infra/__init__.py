from .settings import SettingsLoader  # noqa: F401


class ConfigKey:
    """Известные ключи конфигурации, по которым можно получить конкретное значение."""

    """Базовая валюта."""
    BASE_CURRENCY = "base_currency"

    """Путь к директории с данными."""
    DATA_PATH = "data_path"
