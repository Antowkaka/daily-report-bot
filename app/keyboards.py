from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.text_config import get_text

import app.types as app_types
import app.callback_dates as cb_dates

first_step_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=get_text('btn-set-goals'))],
], one_time_keyboard=True, resize_keyboard=True)

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=get_text('btn-track-your-day'))],
    [KeyboardButton(text=get_text('btn-statistic'))]
], one_time_keyboard=True, resize_keyboard=True)

training_goal_types_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text='1',
        callback_data=cb_dates.TrainingTypeCallbackData(goal_type=app_types.TrainingGoalType.trainings_per_week).pack()
    ),
    InlineKeyboardButton(
        text='2',
        callback_data=cb_dates.TrainingTypeCallbackData(goal_type=app_types.TrainingGoalType.trainings_kcal).pack()
    )
]])

set_custom_goal_skip_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text=get_text('btn-skip-step'),
        callback_data=cb_dates.SkipStepCallbackData(step=app_types.SkipStepType.skip_custom_goal_setting).pack()
    ),
]])

set_custom_goal_complete_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text=get_text('btn-complete'),
        callback_data=cb_dates.CompleteCallbackData(step=app_types.CompleteStepType.complete_custom_goal_setting).pack()
    ),
]])
