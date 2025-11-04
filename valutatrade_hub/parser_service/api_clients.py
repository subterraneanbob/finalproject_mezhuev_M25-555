from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import IntEnum
from http import HTTPStatus

from requests import Response, get
from requests.exceptions import RequestException

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.core.models import ExchangeRate

from .config import ParserConfig


class CoinGeckoStatus(IntEnum):
    """
    Дополнительные HTTP коды ошибок сервиса CoinGecko.
    """

    ACCESS_DENIED = 1020
    MISSING_API_KEY = 10002
    PRO_API_SUBSCRIPTION_REQUIRED = 10005
    INVALID_API_KEY = 10010
    INVALID_API_KEY2 = 10011


class BaseApiClient(ABC):
    """
    Базовый класс клиента для API сервисов для получения данных о курсах обмена
    валют.
    """

    def __init__(self, service_name: str):
        self.config = ParserConfig()
        self.service_name = service_name

    def _check_response(self, response: Response):
        """
        Проверяет стандартные коды HTTP и выбрасывает исключение, если код указывает
        на ошибку.

        Args:
            response (Response): Ответ на HTTP запрос.

        Raises:
            ApiRequestError: Если код указывает, что произошла ошибка.
        """
        error_message = ""
        match response.status_code:
            case HTTPStatus.REQUEST_TIMEOUT:
                error_message = "Ошибка отправки запроса. Проверьте подключение к сети."
            case HTTPStatus.TOO_MANY_REQUESTS:
                error_message = "Достигнут лимит запросов. Повторите попытку позже."
            case HTTPStatus.INTERNAL_SERVER_ERROR | HTTPStatus.SERVICE_UNAVAILABLE:
                error_message = "Сервис недоступен. Повторите попытку позже."
            case HTTPStatus.FORBIDDEN:
                error_message = "Доступ запрещён."
            case code if code >= 400:
                error_message = f"Ошибка при обращении к сервису: {response.reason}"

        if error_message:
            raise ApiRequestError(error_message)

    @abstractmethod
    def fetch_rates(self) -> list[ExchangeRate]:
        """
        Запрашивает курсы обмена для известных валют.

        Raises:
            ApiRequestError: Если в процессе запроса курсов обмена произошла ошибка.

        Returns:
            list[ExchangeRate]: Список полученных курсов обмена валют.
        """
        return []


class CoinGeckoClient(BaseApiClient):
    def __init__(self):
        super().__init__("CoinGecko")

    def _check_response(self, response: Response):
        error_message = ""
        match response.status_code:
            case CoinGeckoStatus.ACCESS_DENIED:
                error_message = "Доступ запрещён."
            case CoinGeckoStatus.PRO_API_SUBSCRIPTION_REQUIRED:
                error_message = "Для использования сервиса требуется платная подписка."
            case (
                CoinGeckoStatus.MISSING_API_KEY
                | CoinGeckoStatus.INVALID_API_KEY
                | CoinGeckoStatus.INVALID_API_KEY2
            ):
                error_message = "Неверный ключ доступа к API."

        if error_message:
            raise ApiRequestError(error_message)

        super()._check_response(response)

    def fetch_rates(self) -> list[ExchangeRate]:
        params = {
            "ids": ",".join(
                self.config.CRYPTO_ID_MAP[code]
                for code in self.config.CRYPTO_CURRENCIES
            ),
            "vs_currencies": self.config.BASE_CURRENCY,
        }

        try:
            response = get(
                self.config.COINGECKO_URL,
                params,
                timeout=self.config.REQUEST_TIMEOUT,
            )
        except RequestException:
            raise ApiRequestError(
                "Не удалось подключиться к сервису. Проверьте подключение к сети."
            )

        self._check_response(response)

        data = response.json()
        coin_to_currency_map = {
            coin: currency for currency, coin in self.config.CRYPTO_ID_MAP.items()
        }
        updated_at = datetime.now(timezone.utc)

        return [
            ExchangeRate(
                coin_to_currency_map[coin].upper(),
                base_currency.upper(),
                float(rate),
                updated_at,
            )
            for coin, rates in data.items()
            for base_currency, rate in rates.items()
        ]


class ExchangeRateApiClient(BaseApiClient):
    def __init__(self):
        super().__init__("ExchangeRateApi")

    def _check_response(self, response: Response):
        super()._check_response(response)

        error_message = ""
        match response.json():
            case {"result": "success"}:
                return
            case {"error-type": error_type}:
                match error_type:
                    case "unsupported-code":
                        error_message = "Неверный код валюты."
                    case "malformed-request":
                        error_message = "Некорректная структура запроса."
                    case "invalid-key":
                        error_message = "Неверный ключ доступа к API."
                    case "inactive-account":
                        error_message = "Необходимо активировать учётную запись."
                    case "quota-reached":
                        error_message = (
                            "Достигнут лимит запросов. Повторите попытку позже."
                        )

        if error_message:
            raise ApiRequestError(error_message)

    def fetch_rates(self) -> list[ExchangeRate]:
        try:
            response = get(
                self.config.EXCHANGERATE_API_URL + self.config.BASE_CURRENCY,
                timeout=self.config.REQUEST_TIMEOUT,
            )
        except RequestException:
            raise ApiRequestError(
                "Не удалось подключиться к сервису. Проверьте подключение к сети."
            )

        self._check_response(response)

        data = response.json()
        rates = data.get("rates", {})
        updated_at_ts = data.get(
            "time_last_update_unix", datetime.now(timezone.utc).timestamp()
        )
        updated_at = datetime.fromtimestamp(updated_at_ts, timezone.utc)
        base_currency = self.config.BASE_CURRENCY

        return [
            ExchangeRate(
                currency.upper(),
                base_currency.upper(),
                float(rate),
                updated_at,
            )
            for currency, rate in rates.items()
            if currency in self.config.FIAT_CURRENCIES
        ]
