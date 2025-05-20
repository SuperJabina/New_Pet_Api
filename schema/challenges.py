from pydantic import BaseModel
from typing import List

class ChallengeSchema(BaseModel):
    id: int
    name: str
    description: str
    status: bool

class ChallengesSchema(BaseModel):
    challenges: List[ChallengeSchema]