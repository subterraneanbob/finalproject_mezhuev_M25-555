import logging
import os
from enum import StrEnum
from logging.handlers import RotatingFileHandler

from valutatrade_hub.infra import Settings


class LogFormat(StrEnum):
    JSON = "json"
    Text = "text"


LOG_LEVEL = logging.INFO
# Формат - JSON или текст
LOG_FORMAT = LogFormat.Text
# Максимальное количество файлов при ротации
LOG_BACKUP_COUNT = 5
# Ротация файлов, если файл больше 2 MiB
LOG_MAX_SIZE = 2 * 1024 * 1024


def setup_logger(name: str):
    settings = Settings()

    os.makedirs(settings.LOG_PATH, exist_ok=True)
    log_file_path = os.path.join(settings.LOG_PATH, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )

    if LOG_FORMAT == LogFormat.JSON:
        formatter = logging.Formatter("%(message)s")
    else:
        formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


parser_service_logger = setup_logger("parser")
actions_logger = setup_logger("actions")
