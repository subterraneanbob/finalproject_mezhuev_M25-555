import inspect
import json
import os
from datetime import datetime
from functools import wraps
from time import time
from typing import Any

from valutatrade_hub.core.utils import format_currency, format_exchange_rate
from valutatrade_hub.infra import ConfigKey, SettingsLoader

from .logging_config import (
    LOG_BACKUP_COUNT,
    LOG_FILE_NAME,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_MAX_SIZE,
    LOG_TIME_LIMIT,
)


def log_action(verbose: bool = False):
    """
    Декоратор для логирования операций.

    Args:
        verbose (bool): Добавлять контекст операции к записи в логе.
    """

    def create_entry(action: str, args, kwargs) -> dict:
        """Создаёт и заполняет новую запись."""

        entry = {}

        entry["level"] = LOG_LEVEL
        entry["timestamp"] = datetime.now().isoformat(timespec="seconds")
        entry["action"] = action

        if user := kwargs.get("user"):
            entry["user"] = user.username

        match args:
            case (str(currency), float(amount)):
                entry["currency"] = currency
                entry["amount"] = amount

        return entry

    def format_text_part(name: str, value: Any) -> str:
        """Форматирует названия и значения."""

        match name:
            case "level" | "timestamp" | "action" | "result":
                return value
            case "amount" | "before" | "after":
                return f"{name}={format_currency(value)}"
            case "rate":
                return f"{name}={format_exchange_rate(value)}"
            case _:
                return f"{name}='{value}'"

    def get_log_file_path() -> str:
        """
        Формирует путь к файлу лога. Создаёт директорию для хранения файлов,
        если она не существует.
        """

        settings = SettingsLoader()
        log_dir = settings.get(ConfigKey.LOG_PATH, "logs")
        os.makedirs(log_dir, exist_ok=True)

        return os.path.join(log_dir, LOG_FILE_NAME)

    def ensure_rotated(file_path: str):
        """
        Производит ротацию лог файлов при необходимости.
        """
        if not os.path.exists(file_path):
            return

        file_size = os.path.getsize(file_path)
        file_last_modified = os.path.getmtime(file_path)

        if file_size > LOG_MAX_SIZE or time() - file_last_modified > LOG_TIME_LIMIT:
            for i in range(LOG_BACKUP_COUNT - 1, 0, -1):
                src = f"{file_path}.{i}"
                dst = f"{file_path}.{i + 1}"
                if os.path.exists(src):
                    os.replace(src, dst)

            os.replace(file_path, f"{file_path}.1")

    def write_log_entry(entry: dict):
        """Добавляет новую запись в лог файл."""

        if LOG_FORMAT == "json":
            line = json.dumps(entry, ensure_ascii=False)
        else:
            line = " ".join(format_text_part(k, v) for k, v in entry.items())

        file_path = get_log_file_path()
        ensure_rotated(file_path)

        with open(file_path, "a", encoding="utf-8") as log_file:
            print(line, file=log_file)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result, error = None, None
            action = func.__name__.upper()
            entry = create_entry(action, args, kwargs)
            context = {}

            try:
                if "context" in inspect.signature(func).parameters:
                    kwargs["context"] = context
                result = func(*args, **kwargs)
            except Exception as ex:
                error = ex
                entry["error_type"] = type(error).__name__
                entry["error_message"] = str(error)

            if verbose and not error:
                entry |= context

            entry["status"] = "ERROR" if error else "OK"
            write_log_entry(entry)

            if error:
                raise error

            return result

        return wrapper

    return decorator
