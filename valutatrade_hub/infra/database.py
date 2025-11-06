import json
import os
from tempfile import NamedTemporaryFile
from typing import Any, Callable

from .settings import Settings, SingletonMeta


class DatabaseManager(metaclass=SingletonMeta):
    """
    Класс для абстракции доступа к хранилищу данных в формате JSON.
    Создаётся только один раз (синглтон).
    """

    def __init__(self):
        """
        Создаёт объект DatabaseManager и директорию, где хранятся данные.
        Путь к директории с данными берётся из конфигурации.
        """
        self.data_path = Settings().DATA_PATH
        os.makedirs(self.data_path, exist_ok=True)

    def load(
        self,
        file_name: str,
        decode_func: Callable | None = None,
        default_func: Callable = list,
    ) -> Any:
        """
        Загружает данные из указанного JSON файла. Для декодирования словарей в
        объекты используется функция `decode_func`. Если файл не найден, то
        возвращаемый объект создаётся переданной функцией.

        Args:
            file_name (str): Имя файла, из которого загружаются данные.
            decode_func (Callable, optional): Функция, которая преобразует переданный
            словарь в определённый объект и возвращает его.
            default_func (Callable, optional): Функция, которая конструирует
            значение, возвращаемое если файл не найден.

        Returns:
            Объект или список, полученный в результате декодирования данных
            из JSON файла.
        """
        file_path = os.path.join(self.data_path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as json_file:
                return json.load(json_file, object_hook=decode_func)
        except FileNotFoundError:
            return default_func()

    def save(
        self,
        file_name: str,
        data,
        encode_func: Callable | None = None,
        use_temp_file: bool = False,
    ):
        """
        Сохраняет объект в указанный файл, пользуясь указанной функцией `encode_func`
        для перевода объектов в словари для записи в формате JSON.

        Args:
            file_name (str): Имя файла, в который данные сохранятся.
            data: Объект или список объектов, которые требуется сохранить.
            encode_func (Callable, optional): Функция, которая преобразует
            переданный объект в словарь и возвращает его.
            use_temp_file (bool, optional): Использовать временный файл для
            сохранения объекта и последующего копирования в место назначения.
        """
        file_path = os.path.join(self.data_path, file_name)
        args = {"default": encode_func, "ensure_ascii": False, "indent": 4}

        if use_temp_file:
            with NamedTemporaryFile("w", encoding="utf-8", delete=False) as temp_file:
                json.dump(data, temp_file, **args)
                temp_file_path = temp_file.name
            os.replace(temp_file_path, file_path)
        else:
            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, **args)
