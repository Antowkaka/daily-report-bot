from typing import Dict, TypedDict

from aiogram.types import User as TgUser


class CustomGoalDict(TypedDict):
    name: str
    goal: int


GoalsType = list[Dict[str, int] | Dict[str, CustomGoalDict]]


class DbUser:
    def __init__(self, tg_user: TgUser, goals: GoalsType = None):
        self._full_name = tg_user.full_name
        self._username = tg_user.username
        self._tg_id = tg_user.id
        self._goals = goals

    @property
    def model(self):
        return {
            'fullName': self._full_name,
            'username': self._username,
            'telegramID': self._tg_id,
            'goals': self._goals
        }

    def update_goals(self, goals: GoalsType):
        self._goals = goals
