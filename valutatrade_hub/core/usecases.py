from datetime import datetime

from .exceptions import InvalidCurrencyError, UnauthorizedError, UsernameTakenError
from .models import ExchangeRates, Portfolio, User
from .utils import format_currency, generate_salt


class UserSession:
    """
    Представляет сессию последнего пользователя, который успешно авторизовался
    в системе.
    """

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._principal = None
        return cls._instance

    def authenticate(self, user: User):
        """
        Запоминает пользователя, который авторизовался.
        """
        self._principal = user

    @property
    def principal(self) -> User | None:
        """
        User or None: Возвращает пользователя, который авторизовался, или None,
        если никто ещё не проходил авторизацию.
        """
        return self._principal


def _check_auth() -> User:
    """
    Проверяет, авторизован ли пользователь.

    Returns:
        User: Текущий авторизованный пользователь.
    """
    session = UserSession()
    if not (user := session.principal):
        raise UnauthorizedError

    return user


def register_user(username: str, password: str) -> int:
    """
    Регистрирует нового пользователя в системе.

    Args:
        username (str): Имя нового пользователя.
        password (str): Пароль нового пользователя.

    Raises:
        UsernameTakenError: Если имя пользователя занято.
        PasswordTooShortError: Если пароль слишком короткий.

    Returns:
        int: Уникальный номер пользователя.
    """
    users = User.load()

    if any(user.username == username for user in users):
        raise UsernameTakenError(username)

    user_id = max([user.user_id for user in users], default=0) + 1
    salt = generate_salt()
    registration_date = datetime.now()

    new_user = User(user_id, username, "", salt, registration_date)
    new_user.change_password(password)

    users.append(new_user)

    portfolios = Portfolio.load()
    portfolios.append(Portfolio(user_id, {}))
    Portfolio.save(portfolios)

    User.save(users)

    return user_id


def login(username: str, password: str):
    """
    Проверяет пароль и авторизует пользователя.

    Args:
        username (str): Имя нового пользователя.
        password (str): Пароль нового пользователя.

    Raises:
        UserNotFoundError: Если пользователь с именем `username` не зарегистрирован.
        IncorrectPasswordError: Если неправильный пароль.
    """

    user = User.find(username)
    user.verify_password(password)

    session = UserSession()
    session.authenticate(user)


def show_portfolio(base_currency: str = "USD"):
    """
    Показывает информацию о всех кошельках и итоговую стоимость в заданной
    валюте (USD по умолчанию).

    Args:
        base_currency (str, optional): Базовая валюта, в которой будет подсчитана
        итоговая стоимость портфеля.

    Raises:
        UnauthorizedError: Если пользователь не залогинен.
    """

    def update_max_width(max_width: int, amount: float) -> int:
        width = len(format_currency(amount))
        return max(max_width, width)

    user = _check_auth()
    portfolio = Portfolio.find(user.user_id)
    wallets = portfolio.wallets

    if not wallets:
        print(f"У пользователя '{user.username}' нет кошельков.")
        return

    exchange_rates = ExchangeRates.load()

    if base_currency not in exchange_rates.currencies:
        raise InvalidCurrencyError(base_currency)

    # Максимальная длина значения баланса в валюте кошелька и в базовой
    # для выравнивания при выводе.
    max_width = 0
    max_width_bc = 0

    total_value = portfolio.get_total_value(exchange_rates, base_currency)

    balances_by_wallet = []
    for currency, wallet in wallets.items():
        balance = wallet.balance
        exchange_rate = exchange_rates.get_exchange_rate(currency, base_currency)
        balance_bс = balance * exchange_rate
        max_width = update_max_width(max_width, balance)
        max_width_bc = update_max_width(max_width_bc, balance_bс)
        balances_by_wallet.append((currency, balance, balance_bс))

    print(f"Портфель пользователя '{user.username}' (база: {base_currency}):")

    for currency, balance, balance_bc in balances_by_wallet:
        print(
            f"- {currency}: {format_currency(balance, width=max_width)} -> "
            f"{format_currency(balance_bc, width=max_width_bc)} {base_currency}"
        )

    print("-----------------------------------")
    print(f"ИТОГО: {format_currency(total_value)} {base_currency}")
