from enum import Enum

class APIRoutes(Enum):
    """
    Маршруты API для ChallengesClient.
    """
    NEW_TOKEN = "/challenger"
    CHALLENGES = "/challenges"
    TODOS = "/todos"