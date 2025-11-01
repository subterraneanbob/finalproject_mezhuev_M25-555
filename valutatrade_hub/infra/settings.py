import tomllib
from typing import Any

PYPROJECT_FILE_PATH = "pyproject.toml"
TOOL = "tool"
SECTION = "valutatrade"


class SingletonMeta(type):
    """
    Метакласс для создания классов, которые могут иметь только один экземпляр.
    Реализация через метакласс удобна из-за простоты: класс описывается
    как обычно, нужно только указать metaclass в определении.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Создаёт только один экземпляр класса, который использует этот метакласс
        в определении.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SettingsLoader(metaclass=SingletonMeta):
    """
    Класс для доступа к конфигурации. Создаётся только один раз (синглтон).

    Attributes:
        file_path (str): Путь к файлу конфигурации.
    """

    def __init__(self, file_path: str = PYPROJECT_FILE_PATH) -> None:
        """
        Создаёт объект SettingsLoader и загружает конфигурацию.
        """
        self._settings = {}
        self.file_path = file_path
        self.reload()

    def reload(self):
        """
        Загружает конфигурацию из файла.
        """
        try:
            with open(self.file_path, "rb") as settings_file:
                data = tomllib.load(settings_file)
            self._settings = data[TOOL][SECTION]
        except (FileNotFoundError, KeyError):
            self._settings = {}

    def get(self, key: str, default: Any = ...) -> Any:
        """
        Возвращает значение конфигурации по ключу.

        Args:
            key (str): Ключ конфигурации, значение для которого нужно получить.
            default (Any, optional): Значение по умолчанию, если ключ не найден.

        Returns:
            Any: Значение конфигурации.
        """
        if default is Ellipsis:
            return self._settings[key]
        return self._settings.get(key, default)
