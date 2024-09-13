from aiogram.fsm.state import StatesGroup, State


class SetGoalsState(StatesGroup):
    diet_goal = State()
    training_goal = State()
    training_goal_type = State()
    sleep_goal = State()
    custom_goal_name = State()
    custom_goal = State()


class TrackDayState(StatesGroup):
    sleep_score = State()
    sleep_details = State()
    diet_score = State()
    diet_details = State()
    training_score = State()
    training_details = State()
