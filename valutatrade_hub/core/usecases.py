from datetime import datetime

from .exceptions import UsernameTakenError
from .models import Portfolio, User
from .utils import generate_salt


class UserSession:
    """
    Представляет сессию последнего пользователя, который успешно авторизовался
    в системе.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._principal = None

    def authenticate(self, user: User):
        """
        Запоминает пользователя, который авторизовался.
        """
        self._principal = user

    @property
    def principal(self) -> User | None:
        """
        User or None: Возвращает пользователя, который авторизовался, или None,
        если никто ещё не проходил авторизацию.
        """
        return self._principal


def register_user(username: str, password: str) -> int:
    """
    Регистрирует нового пользователя в системе.

    Args:
        username (str): Имя нового пользователя.
        password (str): Пароль нового пользователя.

    Raises:
        UsernameTakenError: Если имя пользователя занято.
        PasswordTooShortError: Если пароль слишком короткий.

    Returns:
        int: Уникальный номер пользователя.
    """
    users = User.load()

    if any(user.username == username for user in users):
        raise UsernameTakenError(username)

    user_id = max([user.user_id for user in users], default=0) + 1
    salt = generate_salt()
    registration_date = datetime.now()

    new_user = User(user_id, username, "", salt, registration_date)
    new_user.change_password(password)

    users.append(new_user)

    portfolios = Portfolio.load()
    portfolios.append(Portfolio(user_id, {}))
    Portfolio.save(portfolios)

    User.save(users)

    return user_id


def login(username: str, password: str):
    """
    Проверяет пароль и авторизует пользователя.

    Args:
        username (str): Имя нового пользователя.
        password (str): Пароль нового пользователя.

    Raises:
        UserNotFoundError: Если пользователь с именем `username` не зарегистрирован.
        IncorrectPasswordError: Если неправильный пароль.
    """

    user = User.find(username)
    user.verify_password(password)

    session = UserSession()
    session.authenticate(user)
