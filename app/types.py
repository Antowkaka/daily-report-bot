import enum


class TrainingGoalType(enum.Enum):
    trainings_per_week = 'trainings-per-week'
    trainings_kcal = 'trainings-kcal'


class SkipStepType(enum.Enum):
    skip_custom_goal_setting = 'skip_custom_goal_setting'


class CompleteStepType(enum.Enum):
    complete_custom_goal_setting = 'complete_custom_goal_setting'
