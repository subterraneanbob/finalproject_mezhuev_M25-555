from collections.abc import Iterable
from datetime import datetime

from valutatrade_hub.core.models import ExchangeRate, ExchangeRates
from valutatrade_hub.core.utils import format_datetime_iso
from valutatrade_hub.infra import DatabaseManager

from .config import ParserConfig


class ExchangeRatesStorage:
    """
    Представляет хранилище оперативных и исторических данных о курсах обмена валют.
    """

    def __init__(self):
        self.config = ParserConfig()

    def save_rates(
        self, source: str, last_refresh: datetime, rates: Iterable[ExchangeRate]
    ):
        """
        Сохраняет оперативные курсы обмена валют с указанием источника данных и
        метки времени. Для сохранения выбирается наиболее новое значение для
        каждой валютной пары.

        Args:
            source (str): Источник полученных данных.
            last_refresh (datetime): Время получения данных.
            rates (Iterable[ExchangeRate]): Курсы обмена.
        """
        exchange_rates = ExchangeRates.load()

        exchange_rates.source = source
        exchange_rates.last_refresh = last_refresh
        exchange_rates.update(rates)

        ExchangeRates.save(exchange_rates)

    def save_historical_rates(self, source: str, rates: Iterable[ExchangeRate]):
        """
        Сохраняет исторические значения курсов обмена валют с указанием
        источника данных.

        Args:
            source (str): Источник полученных данных.
            rates (Iterable[ExchangeRate]): Курсы обмена.
        """

        def encode_rates(obj):
            match obj:
                case ExchangeRate():
                    timestamp = format_datetime_iso(obj.updated_at)
                    return {
                        "id": (f"{obj.from_currency}_{obj.to_currency}_{timestamp}"),
                        "from_currency": obj.from_currency,
                        "to_currency": obj.to_currency,
                        "rate": obj.rate,
                        "timestamp": timestamp,
                        "source": source,
                    }
                case _:
                    return obj

        database = DatabaseManager()
        existing_rates = database.load(self.config.HISTORY_FILE, default_func=list)
        existing_rates.extend(rates)
        database.save(
            self.config.HISTORY_FILE,
            existing_rates,
            encode_rates,
            use_temp_file=True,
        )
