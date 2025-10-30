import re
from collections.abc import Iterable
from hashlib import sha256
from os import urandom

from .exceptions import AmountIsNotPositiveError, InvalidCurrencyCode

_CURRENCY_RE = re.compile(r"^[A-Z]{2,5}$")


class AmountMaxWidth:
    """
    Рассчитывает максимальную ширину отформатированного значения валюты для
    вывода на экран.
    """

    def __init__(self, iterable: Iterable[float] | None = None):
        self.max_width = 0

        if iterable:
            for amount in iterable:
                self.update(amount)

    def update(self, amount: float):
        width = len(format_currency(amount))
        self.max_width = max(self.max_width, width)

    def __int__(self):
        return self.max_width


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


def format_exchange_rate(amount: float) -> str:
    """
    Форматирует значение курса обмена валюты.

    Args:
        amount (float): Значение курса обмена валюты.

    Returns:
        str: Отформатированная строка.
    """
    return f"{amount:.6f}"


def validate_currency(currency_code: str):
    """
    Валидирует код валюты.

    Args:
        currency_code (str): Код валюты.

    Raises:
        InvalidCurrencyCode: Если некорректный код валюты.
    """
    if not _CURRENCY_RE.match(currency_code):
        raise InvalidCurrencyCode(currency_code)


def validate_amount(amount: float, attr_name: str = "amount"):
    """
    Проверяет, является ли денежная сумма положительной.

    Args:
        amount (float): Денежная сумма.
        attr_name (str): Названия атрибута, который проверяется, для передачи в
        исключение.

    Raises:
        AmountIsNotPositiveError: Если сумма неположительная.
    """
    if amount <= 0:
        raise AmountIsNotPositiveError(attr_name)
