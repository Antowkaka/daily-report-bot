from typing import Dict
import re

import aiogram.utils.keyboard as keyboard

from app.entities.goal import GoalEntity, GoalChangeAccessType
from app.text_config import get_text
from app.types import TrainingGoalType

import app.types as app_types
import app.callback_dates as cb_dates

all_training_types_btns = {
    TrainingGoalType.trainings_per_week: get_text('btn-edit-training-type-goal-count-week'),
    TrainingGoalType.trainings_kcal: get_text('btn-edit-training-type-goal-kcal-training')
}

first_step_keyboard = keyboard.ReplyKeyboardMarkup(keyboard=[
    [keyboard.KeyboardButton(text=get_text('btn-greeting-keyboard-set-goals'))],
], one_time_keyboard=True, resize_keyboard=True)

main_keyboard = keyboard.ReplyKeyboardMarkup(keyboard=[
    [keyboard.KeyboardButton(text=get_text('btn-main-keyboard-track-your-day'))],
    [keyboard.KeyboardButton(text=get_text('btn-main-keyboard-show-user-goals'))],
    [keyboard.KeyboardButton(text=get_text('btn-main-keyboard-statistic'))]
], one_time_keyboard=True, resize_keyboard=True)

statistic_keyboard = keyboard.ReplyKeyboardMarkup(keyboard=[
    [keyboard.KeyboardButton(text=get_text('btn-statistic-keyboard-text'))],
    [keyboard.KeyboardButton(text=get_text('btn-statistic-keyboard-charts'))],
], one_time_keyboard=True, resize_keyboard=True)

training_goal_types_keyboard = keyboard.InlineKeyboardMarkup(inline_keyboard=[[
    keyboard.InlineKeyboardButton(
        text=all_training_types_btns[TrainingGoalType.trainings_per_week],
        callback_data=cb_dates.TrainingTypeCallbackData(goal_type=app_types.TrainingGoalType.trainings_per_week).pack()
    ),
    keyboard.InlineKeyboardButton(
        text=all_training_types_btns[TrainingGoalType.trainings_kcal],
        callback_data=cb_dates.TrainingTypeCallbackData(goal_type=app_types.TrainingGoalType.trainings_kcal).pack()
    )
]])

set_custom_goal_skip_keyboard = keyboard.InlineKeyboardMarkup(inline_keyboard=[[
    keyboard.InlineKeyboardButton(
        text=get_text('btn-setting-goal-skip-step'),
        callback_data=cb_dates.SkipStepCallbackData(step=app_types.SkipStepType.skip_custom_goal_setting).pack()
    ),
]])

set_custom_goal_complete_keyboard = keyboard.InlineKeyboardMarkup(inline_keyboard=[[
    keyboard.InlineKeyboardButton(
        text=get_text('btn-setting-goal-complete'),
        callback_data=cb_dates.CompleteCallbackData(step=app_types.CompleteStepType.complete_custom_goal_setting).pack()
    ),
]])


training_done_answer_keyboard = keyboard.InlineKeyboardMarkup(inline_keyboard=[
    [keyboard.InlineKeyboardButton(
        text=get_text('btn-track-report-training-done-answer-yes'),
        callback_data=cb_dates.AnswerTrainingDoneCallbackData(answer=True).pack()
    )],
    [keyboard.InlineKeyboardButton(
        text=get_text('btn-track-report-training-done-answer-no'),
        callback_data=cb_dates.AnswerTrainingDoneCallbackData(answer=False).pack()
    )]
])

tracked_result_visualization_options_keyboard = keyboard.InlineKeyboardMarkup(inline_keyboard=[
    [keyboard.InlineKeyboardButton(
        text=get_text('btn-track-report-charts'),
        callback_data=cb_dates.TrackingResultOptionCallbackData(
            option_type=app_types.TrackingResultVisualizationType.charts
        ).pack()
    )],
])


def create_goals_keyboard(goals: Dict[str, GoalEntity.model]) -> keyboard.InlineKeyboardMarkup:
    goals_keyboard = keyboard.InlineKeyboardBuilder()
    goals_items = goals.items()
    last_goal_key = list(goals_items)[-1][0]

    if 'customGoal' in last_goal_key:
        last_custom_goal_index = int(last_goal_key[-1])
        new_goal_key = f'customGoal_{last_custom_goal_index + 1}'
    else:
        new_goal_key = 'customGoal_1'

    # add button for creating new goal
    goals_keyboard.add(keyboard.InlineKeyboardButton(
        text=get_text('btn-create-new-goal'),
        callback_data=cb_dates.EditGoalCallbackData(
            key=new_goal_key,
            name=None,
            is_deletable=True
        ).pack()
    ))

    for goal in goals_items:
        goals_keyboard.add(keyboard.InlineKeyboardButton(
            text=goal[1]['goalName'],
            callback_data=cb_dates.EditGoalCallbackData(
                key=goal[0],
                name=goal[1]['goalName'],
                is_deletable=goal[1]['goalChangeAccess'] == GoalChangeAccessType.deletable.value
            ).pack()
        ))

    return goals_keyboard.adjust(1).as_markup()


def create_goal_menu_keyboard(is_deletable: bool) -> keyboard.ReplyKeyboardMarkup:
    if is_deletable:
        keyboard_buttons = [
            [keyboard.KeyboardButton(text=get_text('btn-edit-goal-keyboard-edit-value'))],
            [keyboard.KeyboardButton(text=get_text('btn-edit-goal-keyboard-delete-goal'))],
            [keyboard.KeyboardButton(text=get_text('btn-edit-goal-keyboard-go-back'))]
        ]
    else:
        keyboard_buttons = [
            [keyboard.KeyboardButton(text=get_text('btn-edit-goal-keyboard-edit-value'))],
            [keyboard.KeyboardButton(text=get_text('btn-edit-goal-keyboard-go-back'))]
        ]

    return keyboard.ReplyKeyboardMarkup(keyboard=keyboard_buttons, one_time_keyboard=True, resize_keyboard=True)


def create_available_training_types_keyboard(current_training_type: str) -> keyboard.InlineKeyboardMarkup:
    available_training_types_btns: list[tuple[TrainingGoalType, str]] = filter(
        lambda btn_dict: btn_dict[0].value != current_training_type,
        list(all_training_types_btns.items())
    )

    keyboard_buttons = []

    for available_btn_dict in available_training_types_btns:
        keyboard_buttons.append([keyboard.InlineKeyboardButton(
            text=available_btn_dict[1],
            callback_data=cb_dates.EditTrainingTypeGoalCallbackData(type=available_btn_dict[0].value).pack()
        )])

    return keyboard.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
