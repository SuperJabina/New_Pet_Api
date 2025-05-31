from pydantic import BaseModel
from typing import List

class ChallengeSchema(BaseModel):
    """
    Схема для представления одного задания в API.

    Определяет структуру данных для отдельного задания с полями id, name, description и status.
    """
    id: int
    name: str
    description: str | None = None # Необязательное поле
    status: bool

    class Config:
        """
        Конфигурация модели Pydantic для ChallengeSchema.
        """
        extra = "forbid"  # Запрещает лишние поля

class ChallengesSchema(BaseModel):
    """
    Схема для представления списка заданий в API.

    Содержит список объектов ChallengeSchema.
    """
    challenges: List[ChallengeSchema]