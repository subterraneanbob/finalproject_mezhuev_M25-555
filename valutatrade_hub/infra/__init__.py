from dataclasses import dataclass

from .settings import SettingsLoader


@dataclass
class Settings:
    BASE_CURRENCY: str
    DATA_PATH: str
    LOG_PATH: str

    def __init__(self):
        settings = SettingsLoader()
        self.BASE_CURRENCY = settings.get("base_currency", "USD")
        self.DATA_PATH = settings.get("data_path", "data/")
        self.LOG_PATH = settings.get("log_path", "logs/")
