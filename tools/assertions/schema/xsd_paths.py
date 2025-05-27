import os
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Получаем абсолютный путь к директории, где находится текущий файл (xsd_paths.py)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class XSDPaths(Enum):
    """
    Пути к XSD-файлам относительно корня проекта.
    """
    CHALLENGES_XSD = os.path.join(CURRENT_DIR, "challenges.xsd")
    TODOS_XSD = os.path.join(CURRENT_DIR, "todos.xsd")

    @property
    def path(self) -> str:
        """
        Возвращает путь к XSD-файлу, проверяя его существование.
        :return: Путь к файлу (str).
        :raises FileNotFoundError: Если файл не существует.
        """
        logger.debug(f"Accessing path: {self.value}")
        if not os.path.exists(self.value):
            raise FileNotFoundError(f"XSD file not found: {self.value}")
        return self.value

