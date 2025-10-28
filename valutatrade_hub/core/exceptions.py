class UserError(Exception):
    pass


class UsernameTakenError(UserError):
    def __init__(self, username: str):
        super().__init__(f"Имя пользователя '{username}' уже занято.")
        self.username = username


class UserNotFoundError(UserError):
    def __init__(self, username: str):
        super().__init__(f"Пользователь '{username}' не найден.")
        self.username = username


class PasswordTooShortError(UserError):
    def __init__(self, min_password_len: int):
        super().__init__(f"Пароль должен быть не короче {min_password_len} символов.")


class IncorrectPasswordError(UserError):
    def __init__(self):
        super().__init__("Неверный пароль.")


class UnauthorizedError(UserError):
    def __init__(self):
        super().__init__("Сначала выполните login.")


class InvalidCurrencyError(UserError):
    def __init__(self, currency: str):
        super().__init__(f"Неизвестная базовая валюта '{currency}'.")
