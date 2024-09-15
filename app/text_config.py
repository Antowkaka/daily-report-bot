import json

from app.loggers import error_logger
from app.types import TrainingGoalType

with open('app/text_data.json', mode='r', encoding='utf-8') as read_file:
    print('file opened')
    text_data = json.load(read_file)


def get_text(key: str) -> str:
    try:
        return text_data[key]
    except KeyError:
        error_logger.error(f'get_text error for key {key}')


def get_training_type_btn_text(training_type: str) -> str:
    match training_type:
        case TrainingGoalType.trainings_per_week.value:
            return get_text('btn-edit-training-type-goal-count-week')
        case TrainingGoalType.trainings_kcal.value:
            return get_text('btn-edit-training-type-goal-kcal-training')
