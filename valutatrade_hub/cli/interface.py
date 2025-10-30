import shlex

from ..core import (
    ApiRequestError,
    CurrencyNotFoundError,
    UserError,
)
from ..core.usecases import (
    buy,
    get_available_currencies,
    get_rate,
    login,
    register_user,
    sell,
    show_portfolio,
)

_QUIT = "quit"  # Команда для выхода


def _parse_amount(float_str: str) -> float | None:
    try:
        return float(float_str)
    except ValueError:
        print("Неверное значение для 'amount'. Введите число.")


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
        return _QUIT


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
            register_user(username, password)
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
        case _:
            print("Неверная команда. Попробуйте снова.")


def run():
    """
    Выполняет основной цикл программы: запрашивает команду у пользователя и
    выполняет её.
    """
    while (command := get_command()) != _QUIT:
        try:
            handle_command(command)
        except ApiRequestError:
            print(
                "Не удаётся получить данные. Проверьте сетевое подключение "
                "и повторите запрос."
            )
        except CurrencyNotFoundError as e:
            print(e)
            get_available_currencies()
        except UserError as e:
            print(e)
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
