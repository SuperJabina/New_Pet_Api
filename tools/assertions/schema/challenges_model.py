from pydantic import BaseModel
from typing import List

class ChallengeSchema(BaseModel):
    id: int
    name: str
    description: str | None = None # Необязательное поле
    status: bool

    class Config:
        extra = "forbid"  # Запрещает лишние поля

class ChallengesSchema(BaseModel):
    challenges: List[ChallengeSchema]