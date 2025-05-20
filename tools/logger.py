import logging

def get_logger(name: str, log_level: str = "DEBUG") -> logging.Logger:
    """
    Создает и настраивает логгер с указанным уровнем логирования.

    Args:
        name: Имя логгера.
        log_level: Уровень логирования (по умолчанию "DEBUG").
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger