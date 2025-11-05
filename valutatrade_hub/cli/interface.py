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
    HELP = "help"


COMMANDS_REFERENCE = {
    Command.REGISTER: (
        "Регистрация нового пользователя.",
        "--username <строка> --password <строка>",
        (
            "--username - имя пользователя (обязателен)",
            "--password - пароль (обязателен)",
        ),
        "--username alice --password 1234",
    ),
    Command.LOGIN: (
        "Авторизация уже существующего пользователя.",
        "--username <строка> --password <строка>",
        (
            "--username - имя пользователя (обязателен)",
            "--password - пароль (обязателен)",
        ),
        "--username alice --password 1234",
    ),
    Command.SHOW_PORTFOLIO: (
        "Печать информации о портфеле пользователя.",
        "--base <строка>",
        ("--base - базовая валюта конвертации (необязателен, по умолчанию USD)",),
        "--base RUB",
    ),
    Command.BUY: (
        "Покупка или зачисление валюты.",
        "--currency <строка> --amount <число>",
        (
            "--currency - код покупаемой валюты (обязателен)",
            "--amount   - сумма покупаемой валюты (обязателен)",
        ),
        "--currency JPY --amount 50000",
    ),
    Command.SELL: (
        "Продажа или вывод валюты.",
        "--currency <строка> --amount <число>",
        (
            "--currency - код продаваемой валюты (обязателен)",
            "--amount   - сумма продаваемой валюты (обязателен)",
        ),
        "--currency EUR --amount 2300",
    ),
    Command.GET_RATE: (
        "Получение курса валюты.",
        "--from <строка> --to <строка>",
        (
            "--from - код исходной валюты (обязателен)",
            "--to   - код целевой валюты (обязателен)",
        ),
        "--from BTC --to USD",
    ),
    Command.UPDATE_RATES: (
        "Обновление курсов обмена валют.",
        "--source <строка>",
        (
            (
                "--source - источник обновления: coingecko или exchangerate "
                "(необязателен, использует все источники по умолчанию)"
            ),
        ),
        "--source coingecko",
    ),
    Command.HELP: ("Показывает справку о команде.", "<команда>", "", ""),
    Command.QUIT: ("Выход из программы.", "", "", ""),
}

ALL_COMMANDS = {c.value for c in Command}


def _parse_amount(float_str: str) -> float | None:
    try:
        return float(float_str)
    except ValueError:
        print("Неверное значение для 'amount'. Введите число.")


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

    description, usage, args, example = COMMANDS_REFERENCE[Command(command)]

    if description:
        print(f"\n{description}")

    print("\nИспользование:\n")
    print(f"   {command} {usage}")

    if args:
        print("\nПараметры:\n")
        for arg in args:
            print(f"   {arg}")

    if example:
        print("\nПример:\n")
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
        case ["register", "--username", username, "--password", password]:
            register(username, password)
        case ["login", "--username", username, "--password", password]:
            login(username, password)
        case ["show-portfolio", "--base", base_currency]:
            show_portfolio(base_currency)
        case ["show-portfolio"]:
            show_portfolio()
        case ["buy", "--currency", currency, "--amount", amount_str]:
            if (amount := _parse_amount(amount_str)) is not None:
                buy(currency, amount)
        case ["sell", "--currency", currency, "--amount", amount_str]:
            if (amount := _parse_amount(amount_str)) is not None:
                sell(currency, amount)
        case ["get-rate", "--from", from_currency, "--to", to_currency]:
            get_rate(from_currency, to_currency)
        case [Command.UPDATE_RATES, "--source", source]:
            update_rates(source)
        case [Command.UPDATE_RATES]:
            update_rates()
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
