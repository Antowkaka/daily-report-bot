from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from text_config import get_text

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=get_text('btn-track-your-day'))],
    [KeyboardButton(text=get_text('btn-statistic'))]
], one_time_keyboard=True, resize_keyboard=True)
