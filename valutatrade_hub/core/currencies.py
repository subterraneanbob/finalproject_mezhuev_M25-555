import re
from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError, InvalidCurrencyCode

FIAT_CURRENCY_DATA = {
    "USD": ("US Dollar", "United States"),
    "EUR": ("Euro", "Eurozone"),
    "JPY": ("Japanese Yen", "Japan"),
    "GBP": ("Pound Sterling", "United Kingdom"),
    "RUB": ("Russian ruble", "Russia"),
}

CRYPTO_CURRENCY_DATA = {
    "BTC": ("Bitcoin", "SHA-256 & ECDSA", 2.20e12),
    "ETH": ("Ethereum", "Gasper", 4.71e11),
    "USDT": ("Tether", "Stablecoin", 1.83e11),
    "XRP": ("XRP (Ripple)", "Ripple Protocol Consensus Algorithm", 1.53e11),
    "BNB": ("Binance Coin", "Proof of Staked Authority", 1.53e11),
}


class Currency(ABC):
    """
    Абстрактный базовый класс для представления валюты.

    Attributes:
        code (str): ISO-код или общепринятый тикер валюты (2-5 символов
        name (str): Человекочитаемое название валюты.
        в верхнем регистре).
    """

    _CURRENCY_RE = re.compile(r"^[A-Z]{2,5}$")

    @classmethod
    def validate_code(cls, currency_code: str):
        """
        Валидирует код валюты.

        Raises:
            InvalidCurrencyCode: Если некорректный код валюты.
        """
        if not cls._CURRENCY_RE.match(currency_code):
            raise InvalidCurrencyCode(currency_code)

    def __init__(self, code: str, name: str):
        Currency.validate_code(code)
        if not name:
            raise ValueError("Название валюты не может быть пустой строкой.")

        self.code = code
        self.name = name

    @abstractmethod
    def get_display_info(self) -> str:
        """
        Возвращает строковое представление валюты.

        Returns:
            str: Строковое представление валюты.
        """
        raise NotImplementedError


class FiatCurrency(Currency):
    """
    Класс, представляющий фиатную валюту.

    Attributes:
        code (str): ISO-код валюты.
        name (str): Человекочитаемое название валюты.
        issuing_country (str): Страна-эмитент.
    """

    def __init__(self, code: str, name: str, issuing_country: str):
        super().__init__(code, name)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    """
    Класс, представляющий криптовалюту.

    Attributes:
        code (str): Общепринятый код валюты.
        name (str): Человекочитаемое название валюты.
        algorithm (str): Алгоритм.
        market_cap (float): Последняя известная капитализация.
    """

    def __init__(self, code: str, name: str, algorithm: str, market_cap: float):
        super().__init__(code, name)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"
        )


def get_currency(code: str) -> Currency:
    """
    Возвращает объект (базовый класс `Currency`) по коду валюты. В зависимости от
    кода, валюта может быть фиатной или крипто-.

    Args:
        code (str): Код валюты.

    Raises:
        CurrencyNotFoundError: Если код валюты неизвестен.

    Returns:
        Currency: Объект, представляющий валюту.
    """

    if code in FIAT_CURRENCY_DATA:
        args = FIAT_CURRENCY_DATA[code]
        return FiatCurrency(code, *args)

    if code in CRYPTO_CURRENCY_DATA:
        args = CRYPTO_CURRENCY_DATA[code]
        return CryptoCurrency(code, *args)

    raise CurrencyNotFoundError(code)
