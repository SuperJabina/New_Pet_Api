from pydantic import BaseModel
from typing import List

class TodoSchema(BaseModel):
    id: int
    title: str
    description: str | None = None # Необязательное поле
    doneStatus: bool

    class Config:
        extra = "forbid"  # Запрещает лишние поля

class TodosSchema(BaseModel):
    todos: List[TodoSchema]