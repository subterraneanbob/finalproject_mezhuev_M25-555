import shlex

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


def parse_command(command: str) -> list[str] | None:
    """
    Разбирает команду на составные части: название команды и параметры (в виде списка).

    Args:
        command (str): Команда для разбора.

    Returns:
        list[str] or None: Составные части команды или None, если разбор не удалось
        произвести.
    """

    try:
        return shlex.split(command)
    except ValueError:
        return None


def run():
    """
    Выполняет основной цикл программы: запрашивает команду у пользователя и
    выполняет её.
    """
    while (command := get_command()) != _QUIT:
        match parse_command(command):
            case _:
                print("Неверная команда. Попробуйте снова.")
