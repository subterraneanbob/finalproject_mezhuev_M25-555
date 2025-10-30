class UserError(Exception):
    """
    Базовый класс для ошибкок, которые происходят из-за неверного ввода
    пользователя.
    """

    pass


class ExchangeRateUnavailableError(UserError):
    """
    Ошибка возникает, когда курс обмена валюты не найден в локальном кеше.
    Выбрасывается в методе `ExchangeRates.get_exchange_rate`.
    """

    def __init__(self, from_currency: str):
        super().__init__(f"Курс обмена для '{from_currency}' не найден в кеше.")


class InsufficientFundsError(UserError):
    """
    Ошибка возникает, если в кошельке недостаточно средств для проведения
    транзакции. Выбрасывается в методе `Wallet.withdraw` и в функции
    `sell` модуля `core.usecases`.
    """

    def __init__(self, currency: str, available: float, required: float):
        message = (
            "Недостаточно средств: "
            f"доступно {available:.2f} {currency}, "
            f"требуется {required:.2f} {currency}"
        )
        super().__init__(message)


class WalletNotFound(UserError):
    """
    Ошибка происходит, если попытаться продать валюту, если кошелёк для неё
    ещё не создан. Выбрасывается в методе `Portfolio.get_wallet` и в функции
    `sell` модуля `core.usecases`.
    """

    def __init__(self, currency: str):
        message = (
            f"У вас нет кошелька '{currency}'. Добавьте валюту: "
            "она создаётся автоматически при первой покупке."
        )
        super().__init__(message)


class CurrencyNotFoundError(UserError):
    """
    Ошибка происходит, если пользователь указал валюту, неизвестную системе.
    Выбрасывается в функции `get_currency` модуля `core.currencies`.
    """

    def __init__(self, currency: str):
        super().__init__(f"Валюта '{currency}' не найдена.")


class InvalidAmountError(UserError):
    """
    Ошибка возникает, если пользователь указал неположительное значение валюты.
    Выбрасывается в методах `Wallet.deposit` и `Wallet.withdraw`, а также
    в функциях `buy`, `sell` модуля `core.usecases`.
    """

    def __init__(self, attr_name: str):
        super().__init__(f"'{attr_name}' должен быть положительным числом.")


class ApiRequestError(Exception):
    """
    Ошибка может произойти, если произошла ошибка при обращении к внешнему API.
    Выбрасывается в слое получения курсов.
    """
