LOG_LEVEL = "INFO"
LOG_FILE_NAME = "actions.log"
LOG_FORMAT = "text"  # text | json
LOG_BACKUP_COUNT = 5  # Максимальное количество логов.

# Политика ротации
LOG_MAX_SIZE = 2 * 1024 * 1024  # Если файл больше 2 MiB.
LOG_TIME_LIMIT = 86400  # Если последняя запись была больше 24 часов назад.
