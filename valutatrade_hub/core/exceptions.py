class UserError(Exception):
    pass


class ExchangeRateUnavailableError(UserError):
    def __init__(self, from_currency: str):
        super().__init__(f"Курс для '{from_currency}' не найден в кеше.")


class InsufficientFundsError(UserError):
    def __init__(self, currency: str, available: float, required: float):
        message = (
            "Недостаточно средств: "
            f"доступно {available:.2f} {currency}, "
            f"требуется {required:.2f} {currency}"
        )
        super().__init__(message)


class WalletNotFound(UserError):
    def __init__(self, currency: str):
        message = (
            f"У вас нет кошелька '{currency}'. Добавьте валюту: "
            "она создаётся автоматически при первой покупке."
        )
        super().__init__(message)


class CurrencyNotFoundError(UserError):
    def __init__(self, currency: str):
        super().__init__(f"Валюта '{currency}' не найдена.")


class InvalidAmountError(UserError):
    def __init__(self, attr_name: str):
        super().__init__(f"'{attr_name}' должен быть положительным числом.")
