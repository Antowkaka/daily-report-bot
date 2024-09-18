from typing import Dict, TypedDict

from aiogram.types import User as TgUser

from app.entities.goal import GoalEntity


GoalsType = Dict[str, GoalEntity.model]


class UserDBModel(TypedDict):
    fullName: str
    username: str
    telegramID: int
    goals: GoalsType


class UserEntity:
    def __init__(self, tg_user: TgUser):
        self._full_name = tg_user.full_name
        self._username = tg_user.username
        self._tg_id = tg_user.id

    @property
    def model(self):
        return {
            'fullName': self._full_name,
            'username': self._username,
            'telegramID': self._tg_id,
            'goals': None  # updates only in DB
        }
