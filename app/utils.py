from typing import Any, Dict
from io import BytesIO
import re
import datetime
import pytz

import matplotlib.pyplot as plt

from app.entities.user import UserDBModel
from app.entities.goal import GoalEntity
from app.entities.report import ReportEntity
from app.text_config import get_text
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


def out_time_tracking(last_report) -> str | None:
    current_datetime = datetime.datetime.now().astimezone(pytz.timezone('Europe/Kyiv'))
    current_date = current_datetime.date()
    current_time = current_datetime.time()

    # 6 p.m.
    def check_is_evening_result() -> str | None:
        return None if current_time >= datetime.time(18, 0) else get_text('message-track-before-evening')

    if last_report and last_report['createdAt'].date() == current_date:
        return get_text('message-track-same-date')
    else:
        return check_is_evening_result()


def validate_last_week_dates(raw_data: list[Dict[str, Any]]) -> int:
    dates = map(lambda x: x['createdAt'].date(), raw_data)
    uniq_dates = set(dates)

    remaining_days = 7 - len(uniq_dates)

    return remaining_days


def prepare_statistic_data(raw_data: list[Dict[str, Any]]):
    prepared_data = {}
    dates = []
    final_data = {
        'item': [],
        'goal': [],
        'dates': [],
        'results': [],
    }

    for raw_report_data in raw_data:
        # get data as string (dd.MM) and push to all dates
        report_created_at_string = raw_report_data['createdAt'].strftime("%d.%m")
        dates.append(report_created_at_string)

        # clear useless fields
        del raw_report_data['createdAt']
        del raw_report_data['_id']

        for key, value in raw_report_data.items():
            if key in prepared_data:
                # update existing items
                prepared_data[key]['maxGoal'] = value['goalValue']
                prepared_data[key]['results'].append({
                    'date': report_created_at_string,
                    'result': value['trackedValue']
                })
            else:
                # set new items
                prepared_data[key] = {}
                prepared_data[key]['title'] = value['title']
                prepared_data[key]['maxGoal'] = value['goalValue']
                prepared_data[key]['results'] = [{
                    'date': report_created_at_string,
                    'result': value['trackedValue']
                }]

    for data in prepared_data.values():
        results = []

        final_data['item'].append(data['title'])
        final_data['goal'].append(data['maxGoal'])
        final_data['dates'].append(dates)

        for existing_result in data['results']:
            results.append(existing_result.get('result') if existing_result.get('date') in dates else 0)

        final_data['results'].append(results)

    return final_data