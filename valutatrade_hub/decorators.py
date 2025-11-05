import inspect
import json
from datetime import datetime, timezone
from functools import wraps
from logging import getLevelName
from typing import Any

from valutatrade_hub.core.utils import (
    format_currency,
    format_datetime_iso,
    format_exchange_rate,
)

from .logging_config import LOG_FORMAT, LOG_LEVEL, LogFormat, actions_logger


def log_action(verbose: bool = False):
    """
    Декоратор для логирования операций.

    Args:
        verbose (bool): Добавлять контекст операции к записи в логе.
    """

    def create_entry(action: str, args, kwargs) -> dict:
        """Создаёт и заполняет новую запись."""

        entry = {}

        if LOG_FORMAT == LogFormat.JSON:
            entry["level"] = getLevelName(LOG_LEVEL)
            entry["timestamp"] = format_datetime_iso(datetime.now(timezone.utc))

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

    def produce_log_entry(entry: dict) -> str:
        """Преобразует запись в строковое представление."""

        if LOG_FORMAT == "json":
            line = json.dumps(entry, ensure_ascii=False)
        else:
            line = " ".join(format_text_part(k, v) for k, v in entry.items())

        return line

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

            log_entry = produce_log_entry(entry)
            if error:
                actions_logger.error(log_entry)
                raise error
            else:
                actions_logger.info(log_entry)

            return result

        return wrapper

    return decorator
