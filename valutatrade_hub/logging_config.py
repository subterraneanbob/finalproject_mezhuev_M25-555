import logging
import os
from logging.handlers import RotatingFileHandler

from valutatrade_hub.infra import Settings

LOG_LEVEL = "INFO"
LOG_LEVEL2 = logging.INFO
LOG_FILE_NAME = "actions.log"
LOG_FORMAT = "text"  # text | json
LOG_BACKUP_COUNT = 5  # Максимальное количество логов.

# Политика ротации
LOG_MAX_SIZE = 2 * 1024 * 1024  # Если файл больше 2 MiB.
LOG_TIME_LIMIT = 86400  # Если последняя запись была больше 24 часов назад.


def setup_logger(name: str):
    settings = Settings()

    os.makedirs(settings.LOG_PATH, exist_ok=True)
    log_file_path = os.path.join(settings.LOG_PATH, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL2)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


parser_service_logger = setup_logger("parser")
actions_logger = setup_logger("actions")
