import os
from dataclasses import dataclass, field


@dataclass
class ParserConfig:
    """
    Конфигурация сервиса для получения данных курсов обмена валют.
    """

    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY") or ""

    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = (
        f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/"
        if EXCHANGERATE_API_KEY
        else "https://open.er-api.com/v6/latest/"
    )

    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "JPY", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "XRP", "BNB", "SOL")
    CRYPTO_ID_MAP: dict = field(
        default_factory=lambda: {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "XRP": "ripple",
            "BNB": "binancecoin",
            "SOL": "solana",
        }
    )

    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    REQUEST_TIMEOUT: int = 10
