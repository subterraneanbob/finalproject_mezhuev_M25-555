import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime

from .currencies import get_currency
from .exceptions import (
    ExchangeRateUnavailableError,
    InsufficientFundsError,
    WalletNotFound,
)
from .utils import get_hashed_password, validate_amount, validate_currency


class User:
    """
    Зарегистрированный пользователь системы.

    Attributes:
        user_id (int): Уникальный номер пользователя
        username (str): Имя пользователя
        hashed_password (str): Хэш пароля пользователя
        salt (str): Уникальная соль для пароля пользователя
        registration_date (datetime): Дата регистрации пользователя
    """

    MIN_PASSWORD_LEN = 4
    DATA_FILE_PATH = "data/users.json"

    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime,
    ):
        self.username = username
        self._user_id = user_id
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @classmethod
    def load(cls, file_path: str = DATA_FILE_PATH) -> list:
        """
        Загружает данные всех пользователей из файла.

        Args:
            file_path (str, optional): Путь к файлу с данными пользователей.
        """

        def decode_user(dct):
            match dct:
                case {"registration_date": reg_date, **args}:
                    reg_date = datetime.fromisoformat(reg_date)
                    return cls(registration_date=reg_date, **args)
                case _:
                    return cls(**dct)

        with open(file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file, object_hook=decode_user)

    @classmethod
    def save(cls, users: list, file_path: str = DATA_FILE_PATH):
        """
        Сохраняет данные всех пользователей в файл.

        Args:
            users (list): Список пользователей типа `User`, который будет сохранён.
            file_path (str, optional): Путь к файлу с данными пользователей.
        """

        def encode_user(obj):
            match obj:
                case User():
                    return {
                        "user_id": obj.user_id,
                        "username": obj.username,
                        "hashed_password": obj.hashed_password,
                        "salt": obj.salt,
                        "registration_date": obj.registration_date.isoformat(),
                    }
                case _:
                    return obj

        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(
                users, json_file, default=encode_user, ensure_ascii=False, indent=4
            )

    @classmethod
    def find(cls, key: int | str, file_path: str = DATA_FILE_PATH):
        """
        Загружает данные пользователя из файла по уникальному ключу:
        по имени пользователя или по его номеру.

        Args:
            key (int or str): Ключ для идентификации пользователя. Для выбора по
            номеру пользователя нужно передать int, по имени пользователя - str.
            file_path (str, optional): Путь к файлу с данными пользователей.
        Raises:
            KeyError: Если пользователь не найден.
        """
        for user in cls.load(file_path):
            if user.user_id == key or user.username == key:
                return user
        raise KeyError(str(key))

    @property
    def user_id(self) -> int:
        """int: Уникальный номер пользователя."""
        return self._user_id

    @property
    def username(self) -> str:
        """str: Имя пользователя."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Изменяет имя пользователя.

        Args:
            value (str): Новое имя пользователя, должно быть не пустым.

        Raises:
            ValueError: Если имя пользователя пустое.
        """
        if not value:
            raise ValueError("Имя не может быть пустым.")

        self._username = value

    @property
    def hashed_password(self) -> str:
        """str: Захешированный пароль."""
        return self._hashed_password

    @property
    def salt(self) -> str:
        """str: Соль для пароля."""
        return self._salt

    @property
    def registration_date(self) -> datetime:
        """datetime: Дата регистрации пользователя."""
        return self._registration_date

    def get_user_info(self):
        """
        Выводит информацию о пользователе.
        """
        print(
            f'Пользователь #{self._user_id}: "{self._username}", '
            f"зарегистрирован {self._registration_date:%Y-%m-%d} "
            f"в {self._registration_date:%H:%M:%S}"
        )

    def change_password(self, new_password: str):
        """
        Изменяет пароль пользователя.

        Args:
            new_password (str): Новый пароль.

        Raises:
            ValueError: Если пароль слишком короткий.
        """
        if len(new_password) < User.MIN_PASSWORD_LEN:
            message = f"Пароль должен быть не короче {User.MIN_PASSWORD_LEN} символов."
            raise ValueError(message)

        self._hashed_password = get_hashed_password(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        """
        Проверяет, верный ли передан пароль.

        Args:
            password (str): Пароль для проверки.

        Returns:
            bool: True, если пароль верный, иначе False.
        """
        return self._hashed_password == get_hashed_password(password, self._salt)


class Wallet:
    """
    Кошелёк пользователя для одной конкретной валюты.

    Attributes:
        currency_code (str): Код валюты (например, "USD" или "BTC").
        balance (float, optional): Баланс в данной валюте (по умолчанию 0.0).
    """

    def __init__(self, currency_code: str, balance: float = 0.0):
        validate_currency(currency_code)
        self.currency_code = currency_code
        self.balance = balance

    @property
    def balance(self) -> float:
        """float: Текущий баланс."""
        return self._balance

    @balance.setter
    def balance(self, value: float | int):
        """Изменяет баланс пользователя.

        Args:
            value (float or int): Новое значения баланса (должно быть неотрицательным).

        Raises:
            TypeError: Если новое значение не типа float или int.
            AmountIsNotPositiveError: Если баланс неположительный.
        """

        if not isinstance(value, (float, int)):
            raise TypeError("Передан неверный тип данных, ожидается int или float.")

        new_balance = float(value)

        if new_balance < 0.0:
            raise ValueError("Баланс не может быть отрицательным.")

        self._balance = new_balance

    def deposit(self, amount: float):
        """
        Пополняет баланс на указанную сумму.

        Args:
            amount (float): Сумма пополнения.

        Raises:
            AmountIsNotPositiveError: Если сумма пополнения неположительная.
        """
        validate_amount(amount)

        self._balance += amount

    def withdraw(self, amount: float):
        """
        Снимает средства, если позволяет баланс.

        Args:
            amount (float): Сумма снятия.

        Raises:
            AmountIsNotPositiveError: Если сумма снятия не положительная.
            InsufficientFundsError: Если сумма снятия превышает текущий баланс.
        """
        validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(self.currency_code, self._balance, amount)

        self._balance -= amount

    def get_balance_info(self):
        """
        Выводит информацию о текущем балансе.
        """
        print(f"Текущий баланс {self.currency_code}: {self.balance:.2f}")


@dataclass
class ExchangeRate:
    """
    Курс обмена валют, актуальный для определённого времени.

    Attributes:
        from_currency (str): Код валюты, которую нужно конвертировать.
        to_currency (str): Код валюты, в которую происходит конвертация.
        rate (float): Курс обмена валюты.
        updated_at (datetime): Время последнего обновления курса.
    """

    from_currency: str
    to_currency: str
    rate: float
    updated_at: datetime

    def reciprocal(self):
        """
        Возвращает новый объект типа ExchangeRate, который представляет курс
        обмена валюты, обратный этому.
        """
        new_rate = 1 / self.rate if self.rate else 0.0
        return ExchangeRate(
            self.to_currency,
            self.from_currency,
            new_rate,
            self.updated_at,
        )

    def __float__(self) -> float:
        return self.rate


class ExchangeRates:
    """
    Доступные курсы обмена валют.

    Attributes:
        source (str): Кто обновил данные.
        last_refresh (datetime): Время последнего обновления курсов.
    """

    DATA_FILE_PATH = "data/rates.json"

    def __init__(
        self,
        source: str,
        last_refresh: datetime,
        rates: dict[tuple[str, str], ExchangeRate],
    ):
        self.source = source
        self.last_refresh = last_refresh
        self._rates = rates

    @classmethod
    def load(cls, file_path: str = DATA_FILE_PATH):
        """
        Загружает курсы валют из файла.

        Args:
            file_path (str, optional): Путь к файлу с курсами валют.
        """

        def decode_rates(dct):
            match dct:
                case {"rate": rate, "updated_at": updated_at}:
                    updated_at = datetime.fromisoformat(updated_at)
                    # Валюты задаются позже при распаковке ключа
                    return ExchangeRate("", "", rate, updated_at)
                case {"source": source, "last_refresh": last_refresh, **rates_data}:
                    last_refresh = datetime.fromisoformat(last_refresh)
                    rates = {}

                    for key, exchange_rate in rates_data.items():
                        currency_pair = tuple(key.split("_", maxsplit=1))
                        exchange_rate.from_currency = currency_pair[0]
                        exchange_rate.to_currency = currency_pair[1]
                        rates[currency_pair] = exchange_rate
                        rates[currency_pair[::-1]] = exchange_rate.reciprocal()

                    return cls(source, last_refresh, rates)
                case _:
                    return dct

        with open(file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file, object_hook=decode_rates)

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> ExchangeRate:
        """
        Возвращает курс обмена для валютной пары.

        Args:
            from_currency (str): Код валюты, которую нужно конвертировать.
            to_currency (str): Код валюты, в которую происходит конвертация.

        Raises:
            CurrencyNotFoundError: Если неизвестный код валюты.
            ExchangeRateUnavailableError: Если курс обмена не доступен.

        Returns:
            ExchangeRate: Объект, реализующий курс обмена валюты, актуальный в
            определённое время.
        """
        validate_currency(from_currency)
        validate_currency(to_currency)

        if from_currency == to_currency:
            return ExchangeRate(from_currency, from_currency, 1.0, datetime.now())

        if (from_currency, to_currency) not in self._rates:
            raise ExchangeRateUnavailableError(from_currency)

        exchange_rate = self._rates[(from_currency, to_currency)]
        return exchange_rate


class Portfolio:
    """
    Портфель кошельков пользователя.

    Attributes:
        user_id (int): Уникальный номер пользователя
        wallets (dict): Словарь кошельков, где ключ - код валюты, а значение - объект
        класса Wallet.
    """

    DATA_FILE_PATH = "data/portfolios.json"

    def __init__(self, user_id: int, wallets: dict[str, Wallet]):
        self._user_id = user_id
        self._wallets = wallets

    @classmethod
    def load(cls, file_path: str = DATA_FILE_PATH):
        """
        Загружает данные о портфелях всех пользователей из файла.

        Args:
            file_path (str, optional): Путь к файлу с портфелям.
        """

        def decode_portfolio(dct):
            match dct:
                case {"currency_code": currency_code, "balance": balance}:
                    return Wallet(currency_code, balance)
                case {"user_id": user_id, "wallets": wallets}:
                    return cls(user_id, wallets)
                case _:
                    return dct

        with open(file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file, object_hook=decode_portfolio)

    @classmethod
    def find(cls, user_id: int, portfolios: list):
        """
        Находит данные о портфеле пользователя по его указанному номеру в
        списке доступных портфелей.

        Args:
            user_id (int): Номер пользователя.
            portfolios (list): Список портфелей.
        """
        for portfolio in portfolios:
            if portfolio._user_id == user_id:
                return portfolio
        raise KeyError("Портфель не найден.")

    @classmethod
    def save(cls, portfolios: list, file_path: str = DATA_FILE_PATH):
        """
        Сохраняет данные о всех портфелях в файл.

        Args:
            portfolios (list): Список портфелей типа `Portfolio`, который будет
            сохранён.
            file_path (str, optional): Путь к файлу с данными пользователей.
        """

        def encode_portfolio(obj):
            match obj:
                case Portfolio():
                    return {
                        "user_id": obj._user_id,
                        "wallets": obj._wallets,
                    }
                case Wallet():
                    return {
                        "currency_code": obj.currency_code,
                        "balance": obj.balance,
                    }
                case _:
                    return obj

        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(
                portfolios,
                json_file,
                default=encode_portfolio,
                ensure_ascii=False,
                indent=4,
            )

    @property
    def user(self) -> User:
        """User: Возвращает объект пользователя."""
        return User.find(self._user_id)

    @property
    def wallets(self) -> dict[str, Wallet]:
        """dict[str, Wallet]: Возвращает копию словаря кошельков."""
        return deepcopy(self._wallets)

    def add_currency(self, currency_code: str):
        """
        Добавляет новый кошелёк в портфель (если его ещё нет).

        Args:
            currency_code (str): Код валюты (например, "USD" или "BTC").
        """
        _ = get_currency(currency_code)

        new_wallet = Wallet(currency_code)
        self._wallets.setdefault(currency_code, new_wallet)

    def get_total_value(
        self, exchange_rates: ExchangeRates, base_currency: str = "USD"
    ) -> float:
        """
        Подсчитывает полную стоимость портфеля в указанной базовой валюте с
        использованием курсов валют.

        Args:
            exchange_rates (dict): Курсы валют
            base_currency (str): Базовая валюта

        Returns:
            float: Полная стоимость портфеля в базовой валюте.
        """
        total = 0.0
        for wallet in self._wallets.values():
            if wallet.currency_code == base_currency:
                total += wallet.balance
            else:
                exchange_rate = exchange_rates.get_exchange_rate(
                    wallet.currency_code, base_currency
                )
                total += wallet.balance * float(exchange_rate)

        return total

    def get_wallet(self, currency_code: str) -> Wallet:
        """
        Возвращает объект класса Wallet по коду валюты.

        Args:
            currency_code (str): Код валюты.

        Returns:
            Wallet: Кошелёк для заданной валюты - объект Wallet.

        """
        if currency_code not in self._wallets:
            raise WalletNotFound(currency_code)

        return self._wallets[currency_code]
