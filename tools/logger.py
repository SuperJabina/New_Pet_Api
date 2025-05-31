import logging

# Инициализация базового логгера для текущего модуля
base_logger = logging.getLogger(__name__)

def get_logger(name: str, log_level: str = "DEBUG") -> logging.Logger:
    """
    Создает и настраивает логгер с указанным уровнем логирования.

    :param name: Имя логгера, обычно соответствует имени модуля
    :param log_level: Уровень логирования (по умолчанию "DEBUG")
    :return: Настроенный объект logging.Logger
    """
    base_logger.info(f"Creating logger with name '{name}' and level '{log_level}'")

    try:
        # Получение или создание логгера с указанным именем
        logger = logging.getLogger(name)

        # Попытка установить уровень логирования
        try:
            logger.setLevel(log_level)
            base_logger.debug(f"Log level set to '{log_level}' for logger '{name}'")
        except ValueError as e:
            base_logger.error(f"Invalid log level '{log_level}': {e}")
            raise ValueError(f"Invalid log level '{log_level}': {e}")

        # Проверка, есть ли уже обработчики, чтобы избежать дублирования
        if not logger.handlers:
            # Создание обработчика для вывода логов в консоль
            handler = logging.StreamHandler()
            # Настройка формата логов
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            # Добавление обработчика к логгеру
            logger.addHandler(handler)
            base_logger.debug(f"Stream handler and formatter added to logger '{name}'")

        base_logger.info(f"Logger '{name}' successfully configured")
        return logger

    except Exception as e:
        # Логирование ошибки при настройке логгера
        base_logger.error(f"Failed to configure logger '{name}': {e}")
        raise