from aiogram.fsm.state import StatesGroup, State


class TrackDayState(StatesGroup):
    sleep_score = State()
    sleep_details = State()
    diet_score = State()
    diet_details = State()
    training_score = State()
    training_details = State()
