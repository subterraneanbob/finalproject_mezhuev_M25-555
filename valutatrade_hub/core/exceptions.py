class UsernameTakenError(Exception):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Имя пользователя '{username}' уже занято.")


class PasswordTooShortError(Exception):
    def __init__(self, min_password_len: int):
        super().__init__(f"Пароль должен быть не короче {min_password_len} символов.")
