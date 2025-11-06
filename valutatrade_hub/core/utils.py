from collections.abc import Callable, Iterable
from datetime import datetime
from hashlib import sha256
from os import urandom

from .exceptions import InvalidAmountError


class MaxWidth:
    """
    Рассчитывает максимальную ширину отформатированного значения для вывода на экран
    с использованием указанной функции преобразования значения в строку.
    """

    def __init__(self, formatter: Callable, iterable: Iterable[float] | None = None):
        self.max_width = 0
        self.formatter = formatter

        if iterable:
            for amount in iterable:
                self.update(amount)

    def update(self, amount: float):
        width = len(self.formatter(amount))
        self.max_width = max(self.max_width, width)

    def __int__(self):
        return self.max_width


def amount_max_width(iterable: Iterable[float] | None = None) -> MaxWidth:
    """
    Создаёт `MaxWidth` для денежных сумм.
    """
    return MaxWidth(format_currency, iterable)


def rate_max_width(iterable: Iterable[float] | None = None) -> MaxWidth:
    """
    Создаёт `MaxWidth` для курса обмена валют.
    """
    return MaxWidth(format_exchange_rate, iterable)


def get_hashed_password(password: str, salt: str) -> str:
    """
    Вычисляет хеш для пароля вместе с указанной солью.
    В качестве хеш-функции используется SHA256.

    Args:
        password (str): Пароль, для которого вычисляется хеш.
        salt (str): Соль для пароля.

    Returns:
        str: Хеш пароля вместе с солью.
    """
    salted_password = salt.encode() + password.encode()
    return sha256(salted_password).hexdigest()


def generate_salt() -> str:
    """
    Генерирует новое случайное значение для соли.

    Returns:
        str: Новое значение соли.
    """
    return urandom(16).hex()


def format_currency(
    amount: float,
    width: int = 0,
    decimal_places: int = 2,
) -> str:
    """
    Форматирует денежное значение.

    Args:
        amount (float): Денежное значение.
        width (int, optional): Общее количество символов. Игнорируется, если длина
        отформатированной строки больше этого значения.
        decimal_places (int, optional): Количество символов после десятичного
        разделителя.

    Returns:
        str: Отформатированная строка.
    """
    return f"{amount:{width}.{decimal_places}f}"


def format_exchange_rate(amount: float, width: int = 0) -> str:
    """
    Форматирует значение курса обмена валюты.

    Args:
        amount (float): Значение курса обмена валюты.
        width (int, optional): Общее количество символов.

    Returns:
        str: Отформатированная строка.
    """
    return f"{amount:{width}.6f}"


def validate_amount(amount: float, attr_name: str = "amount"):
    """
    Проверяет, является ли денежная сумма положительной.

    Args:
        amount (float): Денежная сумма.
        attr_name (str): Названия атрибута, который проверяется, для передачи в
        исключение.

    Raises:
        InvalidAmountError: Если сумма неположительная.
    """
    if amount <= 0:
        raise InvalidAmountError(attr_name)


def format_datetime_iso(datetime: datetime) -> str:
    """
    Форматирует значение `datetime` с точностью до секунды в формате ISO.

    Args:
        datetime (datetime): Объект `datetime`.

    Returns:
        str: Строковое представление объекта `datetime`.
    """
    return datetime.isoformat(timespec="seconds")


def format_datetime(datetime: datetime) -> str:
    """
    Форматирует значение `datetime` с точностью до секунды в виде, удобном для
    чтения человеком.

    Args:
        datetime (datetime): Объект `datetime`.

    Returns:
        str: Строковое представление объекта `datetime`.
    """
    local_time = datetime.astimezone()
    return f"{local_time:%Y-%m-%d %H:%M:%S}"
