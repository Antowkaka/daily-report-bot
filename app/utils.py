from typing import Dict
from io import BytesIO
import matplotlib.pyplot as plt
import re

from app.entities.user import UserDBModel
from app.entities.goal import GoalEntity
from app.entities.report import ReportEntity
from app.types import ReportState


def get_custom_goals(goals: Dict[str, GoalEntity.model]) -> Dict[str, GoalEntity.model]:
    return dict(filter(lambda x: re.search('customGoal', x[0]), goals.items()))


def get_custom_goals_index_part_of_keys(goals: Dict[str, GoalEntity.model]) -> list[int]:
    return [int(re.search(r'\d+', goal_key).group()) for goal_key in goals.keys()]


def process_report(state: ReportState, user: UserDBModel, report: ReportEntity) -> None:
    report_fields = ['diet', 'training', 'sleep']

    main_report_fields = [[key, val] for key, val in state.items() if (lambda x: x in report_fields)(key)]

    if 'custom_reported_goals' in state:
        custom_report_fields = [[key, val] for key, val in state['custom_reported_goals'].items()]
    else:
        custom_report_fields = []

    all_report_fields = [*main_report_fields, *custom_report_fields]

    for [field_name, field_object] in all_report_fields:
        # replace 'user_goal_field' from TempReportObject to 'goal_value' for TrackedReportObject
        field_object['goal_value'] = user['goals'][field_object['user_goal_field']]['goalValue']
        del field_object['user_goal_field']

        report.append_field(field_name, field_object)


def create_chart_image(chart: plt) -> bytes:
    buffer = BytesIO()

    chart.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
    buffer.seek(0)

    return buffer.read()
