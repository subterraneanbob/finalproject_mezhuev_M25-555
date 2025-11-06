import shlex
from enum import StrEnum

from valutatrade_hub.core import (
    ApiRequestError,
    CurrencyNotFoundError,
    UserError,
    buy,
    get_available_currencies,
    get_rate,
    login,
    register,
    sell,
    show_portfolio,
    show_rates,
    update_rates,
)


class Command(StrEnum):
    QUIT = "quit"
    REGISTER = "register"
    LOGIN = "login"
    SHOW_PORTFOLIO = "show-portfolio"
    BUY = "buy"
    SELL = "sell"
    GET_RATE = "get-rate"
    UPDATE_RATES = "update-rates"
    SHOW_RATES = "show-rates"
    HELP = "help"


class Argument(StrEnum):
    USERNAME = "--username"
    PASSWORD = "--password"
    BASE = "--base"
    CURRENCY = "--currency"
    AMOUNT = "--amount"
    FROM = "--from"
    TO = "--to"
    SOURCE = "--source"
    TOP = "--top"


COMMANDS_REFERENCE = {
    Command.REGISTER: (
        "Регистрация нового пользователя.",
        ("--username <строка> --password <строка>",),
        (
            "--username - имя пользователя (обязателен)",
            "--password - пароль (обязателен)",
        ),
        ("--username alice --password 1234",),
    ),
    Command.LOGIN: (
        "Авторизация уже существующего пользователя.",
        ("--username <строка> --password <строка>",),
        (
            "--username - имя пользователя (обязателен)",
            "--password - пароль (обязателен)",
        ),
        ("--username alice --password 1234",),
    ),
    Command.SHOW_PORTFOLIO: (
        "Печать информации о портфеле пользователя.",
        (
            "",
            "--base <строка>",
        ),
        ("--base - базовая валюта конвертации (необязателен, по умолчанию USD)",),
        (
            "",
            "--base RUB",
        ),
    ),
    Command.BUY: (
        "Покупка или зачисление валюты.",
        ("--currency <строка> --amount <число>",),
        (
            "--currency - код покупаемой валюты (обязателен)",
            "--amount   - сумма покупаемой валюты (обязателен)",
        ),
        ("--currency JPY --amount 50000",),
    ),
    Command.SELL: (
        "Продажа или вывод валюты.",
        ("--currency <строка> --amount <число>",),
        (
            "--currency - код продаваемой валюты (обязателен)",
            "--amount   - сумма продаваемой валюты (обязателен)",
        ),
        ("--currency EUR --amount 2300",),
    ),
    Command.GET_RATE: (
        "Получение курса валюты.",
        ("--from <строка> --to <строка>",),
        (
            "--from - код исходной валюты (обязателен)",
            "--to   - код целевой валюты (обязателен)",
        ),
        ("--from BTC --to USD",),
    ),
    Command.UPDATE_RATES: (
        "Обновление курсов обмена валют.",
        (
            "",
            "--source <строка>",
        ),
        (
            (
                "--source - источник обновления: coingecko или exchangerate "
                "(необязателен, использует все источники по умолчанию)"
            ),
        ),
        ("", "--source coingecko", "--source exchangerate"),
    ),
    Command.SHOW_RATES: (
        "Показать список актуальных курсов из локального кэша.",
        (
            "--currency <строка> --base <строка>",
            "--top <число> --base <строка>",
        ),
        (
            "--currency - курс только для указанной валюты",
            "--top      - показать указанное количество самых дорогих криптовалют",
            "--base     - курсы относительно указанной базовой валюты",
        ),
        (
            "",
            "--base EUR",
            "--currency BTC",
            "--currency BTC --base GBP",
            "--top 3",
            "--top 5 --base RUB",
        ),
    ),
    Command.HELP: ("Показывает справку о команде.", ("<команда>",), "", ""),
    Command.QUIT: ("Выход из программы.", "", "", ""),
}

ALL_COMMANDS = {c.value for c in Command}


def _parse_amount(float_str: str) -> float | None:
    try:
        return float(float_str)
    except ValueError:
        print("Неверное значение для параметра 'amount'. Введите число.")


def _parse_top(int_str: str) -> int | None:
    try:
        return int(int_str)
    except ValueError:
        print("Неверное значение для параметра 'top'. Введите целое число.")


def _parse_base(base_args: list[str]) -> str | None:
    match base_args:
        case [Argument.BASE, base]:
            return base
        case []:
            return ""


def print_help():
    print("\nДоступные команды:\n")
    for command, description in COMMANDS_REFERENCE.items():
        print(f"   {command:<14}   {description[0]}")

    print("\nДля получения информации о команде, введите:\n")
    print("   help <команда>")


def print_command_reference(command: str):
    if command not in ALL_COMMANDS:
        print(f"Неизвестная команда: {command}")
        return

    description, usage, args, examples = COMMANDS_REFERENCE[Command(command)]

    if description:
        print(f"\n{description}")

    if usage:
        print("\nИспользование:\n")
        for item in usage:
            print(f"   {command} {item}")

    if args:
        print("\nПараметры:\n")
        for arg in args:
            print(f"   {arg}")

    if examples:
        print("\nПример:\n")
        for example in examples:
            print(f"   {command} {example}")


def get_command() -> str:
    """
    Запрашивает команду у пользователя и возвращает её в виде строки.

    Returns:
        str: Пользовательская команда.
    """

    try:
        while not (user_input := input("\n> ")):
            pass
        return user_input
    except (KeyboardInterrupt, EOFError):
        return Command.QUIT


def handle_command(command: str):
    """
    Разбирает и обрабатывает команду от пользователя.

    Args:
        command (str): Команда от пользователя для обработки.
    """

    try:
        parts = shlex.split(command)
    except ValueError:
        parts = []

    match parts:
        case [Command.REGISTER, Argument.USERNAME, user, Argument.PASSWORD, password]:
            register(user, password)
        case [Command.LOGIN, Argument.USERNAME, user, Argument.PASSWORD, password]:
            login(user, password)
        case [Command.SHOW_PORTFOLIO, Argument.BASE, base_currency]:
            show_portfolio(base_currency)
        case [Command.SHOW_PORTFOLIO]:
            show_portfolio()
        case [Command.BUY, Argument.CURRENCY, currency, Argument.AMOUNT, amount_str]:
            if (amount := _parse_amount(amount_str)) is not None:
                buy(currency, amount)
        case [Command.SELL, Argument.CURRENCY, currency, Argument.AMOUNT, amount_str]:
            if (amount := _parse_amount(amount_str)) is not None:
                sell(currency, amount)
        case [Command.GET_RATE, Argument.FROM, from_currency, Argument.TO, to_currency]:
            get_rate(from_currency, to_currency)
        case [Command.UPDATE_RATES, Argument.SOURCE, source]:
            update_rates(source)
        case [Command.UPDATE_RATES]:
            update_rates()
        case [Command.SHOW_RATES as cmd, Argument.CURRENCY, currency, *base_args] if (
            base := _parse_base(base_args)
        ) is not None:
            show_rates(currency=currency, base_currency=base)
        case [Command.SHOW_RATES as cmd, Argument.TOP, top, *base_args] if (
            base := _parse_base(base_args)
        ) is not None and (top := _parse_top(top)) is not None:
            show_rates(top=top, base_currency=base)
        case [Command.SHOW_RATES as cmd, *base_args] if (
            base := _parse_base(base_args)
        ) is not None:
            show_rates(base_currency=base)
        case [Command.HELP]:
            print_help()
        case [Command.HELP, cmd]:
            print_command_reference(cmd)
        case [cmd, *_] if cmd in ALL_COMMANDS:
            print_command_reference(cmd)
        case _:
            print("Неизвестная команда. Попробуйте снова.")


def run():
    """
    Выполняет основной цикл программы: запрашивает команду у пользователя и
    выполняет её.
    """

    print_help()

    while (command := get_command()) != Command.QUIT:
        try:
            handle_command(command)
        except ApiRequestError as e:
            print(f"Не удаётся получить данные от веб-сервиса. {e}")
        except CurrencyNotFoundError as e:
            print(e)
            get_available_currencies()
        except UserError as e:
            print(e)
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
