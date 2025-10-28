from hashlib import sha256
from os import urandom


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
