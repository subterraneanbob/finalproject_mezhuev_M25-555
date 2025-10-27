import shlex

from ..core.exceptions import UserError
from ..core.usecases import login, register_user

_QUIT = "quit"  # Команда для выхода


def get_command() -> str:
    """
    Запрашивает команду у пользователя и возвращает её в виде строки.

    Returns:
        str: Пользовательская команда.
    """

    try:
        return input("\n> ")
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
            user_id = register_user(username, password)
            print(
                f"Пользователь '{username}' зарегистрирован (id={user_id}). "
                f"Войдите: login --username {username} --password ****"
            )
        case ["login", "--username", username, "--password", password]:
            login(username, password)
            print(f"Вы вошли как '{username}'.")
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
        except UserError as e:
            print(e)
        except Exception as e:
            print("Произошла неизвестная ошибка.")
            print(e)
