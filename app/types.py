import enum
from typing import TypedDict, Dict, NotRequired

from app.entities.goal import GoalEntity
from app.entities.report import TempReportObject
from app.entities.user import UserDBModel


class TrainingGoalType(enum.Enum):
    trainings_per_week = 'trainings-per-week'
    trainings_kcal = 'trainings-kcal'


class SkipStepType(enum.Enum):
    skip_custom_goal_setting = 'skip_custom_goal_setting'


class CompleteStepType(enum.Enum):
    complete_custom_goal_setting = 'complete_custom_goal_setting'


class TrackingResultVisualizationType(enum.Enum):
    charts = 'charts'


class ReportState(TypedDict):
    user: UserDBModel
    diet: TempReportObject
    training: TempReportObject
    sleep: TempReportObject
    charts_data: Dict[str, list[int]]
    custom_goals: NotRequired[Dict[str, GoalEntity.model]]
    custom_goals_indexes: NotRequired[list[int]]
    current_goal_index: NotRequired[int]
    custom_reported_goals: NotRequired[Dict[str, TempReportObject]]