from aiogram.filters.callback_data import CallbackData

from app.types import TrainingGoalType, SkipStepType, CompleteStepType, TrackingResultVisualizationType


class TrainingTypeCallbackData(CallbackData, prefix='training_goal_type'):
    goal_type: TrainingGoalType


class SkipStepCallbackData(CallbackData, prefix='skip_step'):
    step: SkipStepType


class CompleteCallbackData(CallbackData, prefix='complete_step'):
    step: CompleteStepType


class EditGoalCallbackData(CallbackData, prefix='edit_goal'):
    key: str
    name: str | None
    is_deletable: bool


class EditTrainingTypeGoalCallbackData(CallbackData, prefix='edit_training_type'):
    type: str


class AnswerTrainingDoneCallbackData(CallbackData, prefix='training_done_answer'):
    answer: bool


class TrackingResultOptionCallbackData(CallbackData, prefix='chart_data'):
    option_type: TrackingResultVisualizationType
