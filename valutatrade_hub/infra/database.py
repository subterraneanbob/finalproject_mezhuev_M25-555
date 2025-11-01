import json
import os
from typing import Any, Callable

from .settings import SettingsLoader
from .singleton_meta import SingletonMeta


class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self):
        settings = SettingsLoader()
        self.data_path = settings.get("data_path", "data")
        os.makedirs(self.data_path, exist_ok=True)

    def load(
        self,
        file_name: str,
        decode_func: Callable,
        default_func: Callable = list,
    ) -> Any:
        file_path = os.path.join(self.data_path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as json_file:
                return json.load(json_file, object_hook=decode_func)
        except FileNotFoundError:
            return default_func()

    def save(self, file_name: str, data, encode_func: Callable):
        file_path = os.path.join(self.data_path, file_name)
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(
                data,
                json_file,
                default=encode_func,
                ensure_ascii=False,
                indent=4,
            )
