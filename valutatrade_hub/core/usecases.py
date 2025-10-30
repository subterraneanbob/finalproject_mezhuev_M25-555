from datetime import datetime

from .exceptions import UnauthorizedError
from .models import ExchangeRates, Portfolio, User, Wallet
from .utils import (
    AmountMaxWidth,
    format_currency,
    format_exchange_rate,
    generate_salt,
    validate_amount,
    validate_currency,
)


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


def _deposit_base_currency(wallet: Wallet, amount: float):
    """
    Пополняет кошелёк в базовой валюте на указанную сумму и печатает результат.
    """
    currency = wallet.currency_code
    before_amount = wallet.balance
    wallet.deposit(amount)
    after_amount = wallet.balance

    print(f"Пополнение: {format_currency(amount)} {currency}.")
    _print_portfolio_changes((currency, before_amount, after_amount, 0, 0))


def _withdraw_base_currency(wallet: Wallet, amount: float):
    """
    Выводит валюту из кошелька с базовой валютой и печатает результат.
    """
    currency = wallet.currency_code
    before_amount = wallet.balance
    wallet.withdraw(amount)
    after_amount = wallet.balance

    print(f"Снятие: {format_currency(amount)} {currency}.")
    _print_portfolio_changes((currency, before_amount, after_amount, 0, 0))


def _buy_currency(
    wallet: Wallet,
    amount: float,
    wallet_bc: Wallet,
    amount_bc: float,
    rate: float,
):
    """
    Покупает валюту на указанную сумму, расплачиваясь базовой валютой по указанному
    курсу обмена, и печатает результат.
    """
    currency = wallet.currency_code
    base_currency = wallet_bc.currency_code
    before_amount, before_amount_bc = wallet.balance, wallet_bc.balance

    wallet_bc.withdraw(amount_bc)
    wallet.deposit(amount)

    after_amount, after_amount_bc = wallet.balance, wallet_bc.balance

    max_width_before = int(AmountMaxWidth((before_amount, before_amount_bc)))
    max_width_after = int(AmountMaxWidth((after_amount, after_amount_bc)))

    print(
        f"Покупка выполнена: {format_currency(amount)} {currency} "
        f"по курсу {format_exchange_rate(rate)} {base_currency}/{currency}."
    )
    _print_portfolio_changes(
        (
            currency,
            before_amount,
            after_amount,
            max_width_before,
            max_width_after,
        ),
        (
            base_currency,
            before_amount_bc,
            after_amount_bc,
            max_width_before,
            max_width_after,
        ),
    )
    print(f"Оценочная стоимость покупки: {format_currency(amount_bc)} {base_currency}")


def _sell_currency(
    wallet: Wallet,
    amount: float,
    wallet_bc: Wallet,
    amount_bc: float,
    rate: float,
):
    """
    Продаёт валюту на указанную сумму, расплачиваясь базовой валютой по указанному
    курсу обмена, и печатает результат.
    """
    currency = wallet.currency_code
    base_currency = wallet_bc.currency_code
    before_amount, before_amount_bc = wallet.balance, wallet_bc.balance

    wallet.withdraw(amount)
    wallet_bc.deposit(amount_bc)

    after_amount, after_amount_bc = wallet.balance, wallet_bc.balance

    max_width_before = int(AmountMaxWidth((before_amount, before_amount_bc)))
    max_width_after = int(AmountMaxWidth((after_amount, after_amount_bc)))

    print(
        f"Продажа выполнена: {format_currency(amount)} {currency} "
        f"по курсу {format_exchange_rate(rate)} {base_currency}/{currency}."
    )
    _print_portfolio_changes(
        (
            currency,
            before_amount,
            after_amount,
            max_width_before,
            max_width_after,
        ),
        (
            base_currency,
            before_amount_bc,
            after_amount_bc,
            max_width_before,
            max_width_after,
        ),
    )
    print(f"Оценочная выручка: {format_currency(amount_bc)} {base_currency}")


def _print_portfolio_changes(*args: tuple[str, float, float, int, int]):
    """
    Печатает изменения, которые произошли в кошельках после операции.
    """
    if not args:
        return

    print("Изменения в портфеле:")
    for currency, before, after, max_width_before, max_width_after in args:
        print(
            f"- {currency}: было "
            f"{format_currency(before, width=max_width_before)}"
            " -> стало "
            f"{format_currency(after, width=max_width_after)}"
        )


def register_user(username: str, password: str):
    """
    Регистрирует нового пользователя в системе.

    Args:
        username (str): Имя нового пользователя.
        password (str): Пароль нового пользователя.

    Raises:
        ValueError: Если имя пользователя пустое.
        UsernameTakenError: Если имя пользователя занято.
        PasswordTooShortError: Если пароль слишком короткий.
    """

    if not username:
        print("Имя пользователя не может быть пустым.")
        return

    if len(password) < User.MIN_PASSWORD_LEN:
        print(f"Пароль должен быть не короче {User.MIN_PASSWORD_LEN} символов.")
        return

    users = User.load()
    if any(user.username == username for user in users):
        print(f"Имя пользователя '{username}' уже занято.")
        return

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

    print(
        f"Пользователь '{username}' зарегистрирован (id={user_id}). "
        f"Войдите: login --username {username} --password ****"
    )


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

    validate_currency(base_currency)

    user = _check_auth()
    portfolio = Portfolio.find(user.user_id, Portfolio.load())
    wallets = portfolio.wallets

    if not wallets:
        print(f"У пользователя '{user.username}' нет кошельков.")
        return

    # Максимальная длина значения баланса в валюте кошелька и в базовой
    # для выравнивания при выводе.
    max_width = AmountMaxWidth()
    max_width_bc = AmountMaxWidth()

    exchange_rates = ExchangeRates.load()
    total_value = portfolio.get_total_value(exchange_rates, base_currency)

    balances_by_wallet = []
    for currency, wallet in wallets.items():
        balance = wallet.balance
        exchange_rate = exchange_rates.get_exchange_rate(currency, base_currency)
        balance_bс = balance * float(exchange_rate)
        max_width.update(balance)
        max_width_bc.update(balance_bс)
        balances_by_wallet.append((currency, balance, balance_bс))

    print(f"Портфель пользователя '{user.username}' (база: {base_currency}):")

    for currency, balance, balance_bc in balances_by_wallet:
        print(
            f"- {currency}: {format_currency(balance, width=int(max_width))} -> "
            f"{format_currency(balance_bc, width=int(max_width_bc))} {base_currency}"
        )

    print("-----------------------------------")
    print(f"ИТОГО: {format_currency(total_value)} {base_currency}")


def buy(currency: str, amount: float, base_currency: str = "USD"):
    """
    Покупает указанное количество валюты. Если указана базовая валюта в качестве
    валюты покупки, тогда пополняет баланс кошелька в базовой валюте на
    указанную сумму.

    Args:
        currency (str): Код валюты, в которой совершается покупка.
        amount (float): Количество покупаемой валюты.
        base_currency (str, optional): Базовая валюта.

    Raises:
        AmountIsNegativeError: Если отрицательная сумма покупки.
        UnauthorizedError: Если пользователь не залогинен.
        InvalidCurrencyError: Если указана неизвестная валюта.
        ExchangeRateUnavailableError: Если недоступен курс обмена валют.
    """

    validate_currency(currency)
    validate_currency(base_currency)
    validate_amount(amount)
    user = _check_auth()

    exchange_rates = ExchangeRates.load()
    rate = float(exchange_rates.get_exchange_rate(currency, base_currency))

    portfolios = Portfolio.load()
    portfolio = Portfolio.find(user.user_id, portfolios)
    portfolio.add_currency(currency)
    wallet = portfolio.get_wallet(currency)

    if currency == base_currency:
        # Пополнение кошелька
        _deposit_base_currency(wallet, amount)
    else:
        # Покупка валюты
        portfolio.add_currency(base_currency)
        wallet_bc = portfolio.get_wallet(base_currency)
        amount_bc = amount * rate

        _buy_currency(wallet, amount, wallet_bc, amount_bc, rate)

    Portfolio.save(portfolios)


def sell(currency: str, amount: float, base_currency: str = "USD"):
    """
    Продаёт указанное количество валюты. Если указана базовая валюта в качестве
    валюты покупки, тогда списывает сумму с баланса кошелька с базовой валютой.

    Args:
        currency (str): Код валюты, в которой совершается покупка.
        amount (float): Количество покупаемой валюты.
        base_currency (str, optional): Базовая валюта.

    Raises:
        AmountIsNegativeError: Если отрицательная сумма покупки.
        UnauthorizedError: Если пользователь не залогинен.
        InvalidCurrencyError: Если указана неизвестная валюта.
        ExchangeRateUnavailableError: Если недоступен курс обмена валют.
    """
    validate_currency(currency)
    validate_currency(base_currency)
    validate_amount(amount)
    user = _check_auth()

    exchange_rates = ExchangeRates.load()
    rate = float(exchange_rates.get_exchange_rate(currency, base_currency))

    portfolios = Portfolio.load()
    portfolio = Portfolio.find(user.user_id, portfolios)
    wallet = portfolio.get_wallet(currency)

    if currency == base_currency:
        # Вывод с кошелька
        _withdraw_base_currency(wallet, amount)
    else:
        # Продажа валюты
        wallet_bc = portfolio.get_wallet(base_currency)
        amount_bc = amount * rate

        _sell_currency(wallet, amount, wallet_bc, amount_bc, rate)

    Portfolio.save(portfolios)


def get_rate(from_currency: str, to_currency: str):
    """
    Получает текущий курс обмена одной валюты на другую.

    Args:
        from_currency (str): Код исходной валюты.
        to_currency (str): Код целевой валюты.
    """
    validate_currency(from_currency)
    validate_currency(to_currency)

    exchange_rates = ExchangeRates.load()
    exchange_rate = exchange_rates.get_exchange_rate(from_currency, to_currency)

    rate = float(exchange_rate)
    reciprocal_rate = float(exchange_rate.reciprocal())
    updated_at = exchange_rate.updated_at

    print(
        f"Курс {from_currency}->{to_currency}: {format_exchange_rate(rate)} "
        f"(обновлено: {updated_at:%Y-%m-%d %H:%M:%S})"
    )

    print(
        f"Обратный курс {to_currency}->{from_currency}: "
        f"{format_exchange_rate(reciprocal_rate)}"
    )
