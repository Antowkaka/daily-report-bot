from datetime import datetime
from typing import TypedDict, Dict


class BaseTrackedReportObject(TypedDict):
    title: str
    tracked_value: int
    color: str


class TrackedReportObject(BaseTrackedReportObject):
    goal_value: int


class TempReportObject(BaseTrackedReportObject):
    user_goal_field: str


class ReportEntity:
    _report_fields: list[[str, TrackedReportObject]]
    _created_at: datetime

    def __init__(self, user_tg_id: int):
        self._user_tg_id = user_tg_id
        self._report_fields = []

    def set_created_at(self, created_at: datetime):
        self._created_at = created_at

    def append_field(self, field_name: str, field: TrackedReportObject):
        self._report_fields.append([field_name, field])

    @property
    def date(self) -> datetime | None:
        return self._created_at

    @property
    def model(self):
        final_model = {}

        for field in self._report_fields:
            final_model[field[0]] = ReportEntity.create_field_model(field[1])

        final_model['userTelegramID'] = self._user_tg_id
        final_model['createdAt'] = self._created_at

        return final_model

    @property
    def charts_data(self) -> Dict[str, list[int]]:
        titles = []
        tracked_values = []
        goal_values = []

        for field in self._report_fields:
            report_obj: TrackedReportObject = field[1]

            titles.append(report_obj['title'])
            tracked_values.append(report_obj['tracked_value'])
            goal_values.append(report_obj['goal_value'])

        return {
            'name': titles,
            'tracked_value': tracked_values,
            'goal_value': goal_values,
        }

    @staticmethod
    def create_field_model(field: TrackedReportObject):
        return {
            'title': field['title'],
            'trackedValue': field['tracked_value'],
            'goalValue': field['goal_value'],
            'color': field['color'],
        }
