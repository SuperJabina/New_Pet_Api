from pydantic import BaseModel
from typing import List

class TodoSchema(BaseModel):
    """
    Схема для представления одной задачи в API.

    Определяет структуру данных для отдельной задачи с полями id, title, description и doneStatus.
    """
    id: int
    title: str
    description: str | None = None # Необязательное поле
    doneStatus: bool

    class Config:
        """
        Конфигурация модели Pydantic для TodoSchema.
        """
        extra = "forbid"  # Запрещает лишние поля

class TodosSchema(BaseModel):
    """
    Схема для представления списка задач в API.

    Содержит список объектов TodoSchema.
    """
    todos: List[TodoSchema]