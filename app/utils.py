import re
from typing import Dict

from app.entities.user import GoalsType


def convert_goals_row_dict_to_db_goals(goals: Dict[str, int | str]) -> GoalsType:
    db_goals = list()

    def create_custom_field_name_setter(field_value: int | str):
        def _(custom_db_field_name: str):
            db_goals.append({custom_db_field_name: field_value})

        return _

    for goal in goals.items():
        key = goal[0]
        custom_field_setter = create_custom_field_name_setter(goal[1])

        if re.search('custom_goal', key):
            custom_field_setter(f'customGoal_{key[-1]}')
        else:
            match key:
                case 'diet_goal':
                    custom_field_setter('dietGoal')
                case 'training_goal':
                    custom_field_setter('trainingGoal')
                case 'training_goal_type':
                    custom_field_setter('trainingGoalType')
                case 'sleep_goal':
                    custom_field_setter('sleepGoal')

    return db_goals
