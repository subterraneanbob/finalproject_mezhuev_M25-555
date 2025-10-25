from datetime import datetime

from .utils import get_hashed_password


class User:
    """
    Зарегистрированный пользователь системы.

    Attributes:
        user_id (int): Уникальный номер пользователя
        username (str): Имя пользователя
        hashed_password (str): Хэш пароля пользователя
        salt (str): Уникальная соль для пароля пользователя
        registration_date (datetime): Дата регистрации пользователя
    """

    MIN_PASSWORD_LEN = 4

    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime,
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        """int: Уникальный номер пользователя."""
        return self._user_id

    @property
    def username(self) -> str:
        """str: Имя пользователя."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Изменяет имя пользователя.

        Args:
            value (str): Новое имя пользователя, должно быть не пустым.

        Raises:
            ValueError: Если имя пользователя пустое.
        """
        if not value:
            raise ValueError("Имя не может быть пустым.")

        self._username = value

    @property
    def hashed_password(self) -> str:
        """str: Захешированный пароль."""
        return self._hashed_password

    @property
    def salt(self) -> str:
        """str: Соль для пароля."""
        return self._salt

    @property
    def registration_date(self) -> datetime:
        """datetime: Дата регистрации пользователя."""
        return self._registration_date

    def get_user_info(self):
        """
        Выводит информацию о пользователе.
        """
        print(
            f'Пользователь #{self._user_id}: "{self._username}", '
            f"зарегистрирован {self._registration_date:%Y-%m-%d} "
            f"в {self._registration_date:%H:%M:%S}"
        )

    def change_password(self, new_password: str):
        """
        Изменяет пароль пользователя.

        Args:
            new_password (str): Новый пароль.
        """
        if not new_password or len(new_password) < User.MIN_PASSWORD_LEN:
            raise ValueError(
                f"Пароль должен быть не короче {User.MIN_PASSWORD_LEN} символов."
            )

        self._hashed_password = get_hashed_password(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        """
        Проверяет, верный ли передан пароль.

        Args:
            password (str): Пароль для проверки.
        Returns:
            bool: True, если пароль верный, иначе False.
        """
        return self._hashed_password == get_hashed_password(password, self._salt)
