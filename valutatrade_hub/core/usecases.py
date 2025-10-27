from datetime import datetime

from .exceptions import PasswordTooShortError, UsernameTakenError
from .models import User
from .utils import generate_salt, get_hashed_password


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
