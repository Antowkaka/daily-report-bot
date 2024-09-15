import enum
from typing import TypedDict


class GoalChangeAccessType(enum.Enum):
    editable = 'editable'
    deletable = 'deletable'


class GoalDict(TypedDict):
    name: str
    value: int | None
    change_access: GoalChangeAccessType


class GoalEntity:
    def __init__(self, goal: GoalDict):
        self._goal_name = goal['name']
        self._goal_value = goal['value']
        self._goal_change_access = goal['change_access']

    def update_value(self, value: int):
        self._goal_value = value

    @property
    def name(self):
        return self._goal_name

    @property
    def model(self):
        return {
            'goalName': self._goal_name,
            'goalValue': self._goal_value,
            'goalChangeAccess': self._goal_change_access,
        }
