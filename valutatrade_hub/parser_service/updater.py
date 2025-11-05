from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.logging_config import parser_service_logger as logger

from .api_clients import BaseApiClient, CoinGeckoClient, ExchangeRateApiClient
from .storage import ExchangeRatesStorage


@dataclass
class UpdateResult:
    """
    Результат взаимодействия с внешними сервисами при выполнении обновления
    курсов валют.
    """

    last_refresh: datetime
    has_errors = False
    rates_updated: int = 0


class RatesUpdater:
    """
    Класс для выполнения процесса обновления курсов обмена валют, используя
    внешние сервисы, и сохранения полученных данных.
    """

    def __init__(
        self,
        clients: Iterable[BaseApiClient],
        storage: ExchangeRatesStorage,
    ):
        self._clients = iter(clients)
        self._storage = storage

    def run_update(self) -> UpdateResult:
        """
        Выполняет процесс обновления курсов валют.

        Returns:
            UpdateResult: Результат обновления.
        """

        all_rates = []
        last_refresh = datetime.now(timezone.utc)
        result = UpdateResult(last_refresh)

        logger.info("Запуск обновления курсов валют...")

        for client in self._clients:
            try:
                rates = client.fetch_rates()
            except ApiRequestError as e:
                result.has_errors = True
                logger.error(
                    f"Не удалось получить данные от {client.service_name}. {e}"
                )
                continue

            logger.info(
                f"Получаем данные из {client.service_name}... OK ({len(rates)} записей)"
            )

            self._storage.save_historical_rates(client.service_name, rates)
            all_rates.extend(rates)

        result.rates_updated = len(all_rates)
        logger.info(f"Сохраняем {result.rates_updated} записей о курсах обмена валют.")

        self._storage.save_rates("ParserService", last_refresh, all_rates)

        return result


class UpdateSource(StrEnum):
    COINGECKO = "coingecko"
    EXCHANGERATE = "exchangerate"
    ALL = ""


def get_updater(source: UpdateSource = UpdateSource.ALL) -> RatesUpdater:
    """
    Создаёт новый объект для обновления курсов обмена валют.

    Args:
        source (UpdateSource, optional): Источники обновления.
    """
    match source:
        case UpdateSource.COINGECKO:
            clients = [CoinGeckoClient()]
        case UpdateSource.EXCHANGERATE:
            clients = [ExchangeRateApiClient()]
        case _:
            clients = [CoinGeckoClient(), ExchangeRateApiClient()]

    storage = ExchangeRatesStorage()
    return RatesUpdater(clients, storage)
