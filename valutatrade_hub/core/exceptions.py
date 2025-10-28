from .utils import format_currency


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


class InvalidBaseCurrencyError(UserError):
    def __init__(self, currency: str):
        super().__init__(f"Неизвестная базовая валюта '{currency}'.")


class InvalidCurrencyError(UserError):
    def __init__(self, currency: str):
        super().__init__(f"Неизвестная валюта '{currency}'.")


class ExchangeRateUnavailableError(UserError):
    def __init__(self, from_currency: str, to_currency: str):
        super().__init__(
            f"Не удалось получить курс для {from_currency} -> {to_currency}."
        )


class AmountIsNotPositiveError(UserError):
    def __init__(self, arg_name: str):
        super().__init__(f"'{arg_name}' должен быть положительным числом.")


class InvalidCurrencyCode(UserError):
    def __init__(self, currency: str):
        super().__init__(f"Неверный код валюты '{currency}'.")


class InsufficientFundsError(UserError):
    def __init__(self, currency: str, available: float, required: float):
        message = (
            "Недостаточно средств: "
            f"доступно {format_currency(available)} {currency}, "
            f"требуется {format_currency(required)} {currency}"
        )
        super().__init__(message)


class WalletNotFound(UserError):
    def __init__(self, currency: str):
        message = (
            f"У вас нет кошелька '{currency}'. Добавьте валюту: "
            "она создаётся автоматически при первой покупке."
        )
        super().__init__(message)
