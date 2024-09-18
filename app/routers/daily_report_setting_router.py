from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database.db_service import DatabaseService
from app.states import TrackDayState
from app.filters import FilterGoalValue, FilterTextMessage
from app.text_config import get_text
from app.callback_dates import AnswerTrainingDoneCallbackData
from app.entities.user import UserEntity, UserDBModel
from app.entities.report import ReportEntity
from app.types import TrainingGoalType, ReportState
from app.utils import get_custom_goals, get_custom_goals_index_part_of_keys, process_report

import app.keyboards as k_boards

daily_report_setting_router = Router()

"""
During "report" flow I need to use some helper fields in state
but in final stage, when I pass reported data to database I need to clear
my state (state uses as database model) from these helper fields.

I need to maintain state type with these helper fields in one place and don't forget
about it when this flow will be changed.
I decided to extract function for processing final result to app/utils - 'process_report()'
and this function will use ReportState type.

Note! Don't forget to add new helper fields to ReportState type (types.py) and
also check TempReportObject inside app/entities/report.py
"""


# track diet report flow
@daily_report_setting_router.message(TrackDayState.diet_score, FilterTextMessage(), FilterGoalValue())
async def track_diet_report_value_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    user: UserDBModel = data['user']

    await state.update_data(report=ReportEntity())
    await state.update_data({'diet': {
        'title': 'їжа',
        'tracked_value': int(message.text),
        'color': 'red',
        'user_goal_field': 'dietGoal',
    }})

    match user['goals']['trainingGoalType']['goalValue']:
        case TrainingGoalType.trainings_per_week.value:
            text = f'{get_text('message-track-training')} {get_text('message-track-training-option-1')}'
            await state.set_state(TrackDayState.training_score_is_done)
            await message.answer(text, reply_markup=k_boards.training_done_answer_keyboard)
        case TrainingGoalType.trainings_kcal.value:
            text = f'{get_text('message-track-training')} {get_text('message-track-training-option-2')}'
            await state.set_state(TrackDayState.training_score_kcal)
            await message.answer(text)


# track training report flow
@daily_report_setting_router.callback_query(
    TrackDayState.training_score_is_done,
    AnswerTrainingDoneCallbackData.filter()
)
async def track_is_training_done_report_value_handler(
    callback: CallbackQuery,
    callback_data: AnswerTrainingDoneCallbackData,
    state: FSMContext
) -> None:
    await state.update_data({'training': {
        'title': 'кількість тренувань',
        'tracked_value': callback_data.answer if 1 else 0,
        'color': 'green',
        'user_goal_field': 'trainingGoal',
    }})

    await state.set_state(TrackDayState.sleep_score)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(get_text('message-track-sleep'))


@daily_report_setting_router.message(TrackDayState.training_score_kcal, FilterTextMessage(), FilterGoalValue())
async def track_training_kcal_report_value_handler(message: Message, state: FSMContext) -> None:
    await state.update_data({'training': {
        'title': 'тренування',
        'tracked_value': int(message.text),
        'color': 'green',
        'user_goal_field': 'trainingGoal',
    }})

    await state.set_state(TrackDayState.sleep_score)
    await message.answer(get_text('message-track-sleep'))


# track sleep report flow
@daily_report_setting_router.message(TrackDayState.sleep_score, FilterTextMessage(), FilterGoalValue())
async def track_sleep_report_value_handler(
    message: Message,
    state: FSMContext,
    database: DatabaseService
) -> None:
    await state.update_data({'sleep': {
        'title': 'сон',
        'tracked_value': int(message.text),
        'color': 'yellow',
        'user_goal_field': 'sleepGoal',
    }})
    data: ReportState = await state.get_data()

    user: UserDBModel = data['user']

    custom_goals = get_custom_goals(user['goals'])
    custom_goals_indexes = get_custom_goals_index_part_of_keys(custom_goals)

    if len(custom_goals) == 0:
        report: ReportEntity = data['report']

        # process result data
        process_report(data, user, report)

        await database.create_report(report)
        await state.clear()
        await state.update_data(user=user)
        await message.answer(get_text('message-track-successfully'), reply_markup=k_boards.main_keyboard)
    else:
        await state.set_state(TrackDayState.custom_score)
        await state.update_data(current_goal_index=0)
        await state.update_data(custom_goals=custom_goals)
        await state.update_data(custom_goals_indexes=custom_goals_indexes)
        await state.update_data(custom_reported_goals={})
        goal_key = custom_goals_indexes[0]
        text = f'{get_text('template-track-custom')} {custom_goals[f'customGoal_{goal_key}']['goalName']}'
        await message.answer(text)


# track custom report flow
@daily_report_setting_router.message(TrackDayState.custom_score, FilterTextMessage(), FilterGoalValue())
async def track_custom_report_value_handler(
        message: Message,
        state: FSMContext,
        database: DatabaseService
) -> None:
    data: ReportState = await state.get_data()

    custom_goals_indexes = data['custom_goals_indexes']
    current_goal_index = data['current_goal_index']
    current_goal_index_key_part = custom_goals_indexes[current_goal_index]
    current_goal_key = f'customGoal_{current_goal_index_key_part}'
    custom_reported_goals = data['custom_reported_goals']

    # set new custom report
    custom_reported_goals[f'custom_{current_goal_index_key_part}'] = {
        'title': data['custom_goals'][current_goal_key]['goalName'],
        'tracked_value': int(message.text),
        'color': 'blue',
        'user_goal_field': current_goal_key,
    }

    await state.update_data({'custom_reported_goals': custom_reported_goals})

    # index starts from 0, there we start from 1
    if current_goal_index + 1 == len(custom_goals_indexes):
        # retrieve fresh data
        data = await state.get_data()

        # get user for future using
        user: UserDBModel = data['user']
        report: ReportEntity = data['report']

        # process result data
        process_report(data, user, report)

        await database.create_report(report)
        await state.clear()
        await state.update_data(user=user)
        await message.answer(get_text('message-track-successfully'), reply_markup=k_boards.main_keyboard)
    else:
        next_goal_index = current_goal_index + 1
        await state.update_data(current_goal_index=next_goal_index)

        next_goal_index_key_part = custom_goals_indexes[next_goal_index]
        next_goal_key = f'customGoal_{next_goal_index_key_part}'
        text = f'{get_text('template-track-custom')} {data['custom_goals'][next_goal_key]['goalName']}'
        await message.answer(text)
