from datetime import datetime

from .exceptions import PasswordTooShortError, UsernameTakenError
from .models import User
from .utils import generate_salt, get_hashed_password


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


def register_user(username: str, password: str):
    """
    Регистрирует нового пользователя в системе.

    Args:
        username (str): Имя нового пользователя.
        password (str): Пароль нового пользователя.

    Raises:
        UsernameTakenError: Если имя пользователя занято.
        PasswordTooShortError: Если пароль слишком короткий.
    """
    users = User.load()

    if any(user.username == username for user in users):
        raise UsernameTakenError(username)

    if len(password) < User.MIN_PASSWORD_LEN:
        raise PasswordTooShortError(User.MIN_PASSWORD_LEN)

    user_id = max([user.user_id for user in users], default=0) + 1
    salt = generate_salt()
    hashed_password = get_hashed_password(password, salt)
    registration_date = datetime.now()

    new_user = User(user_id, username, hashed_password, salt, registration_date)
    users.append(new_user)

    User.save(users)


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
