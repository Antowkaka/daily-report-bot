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
    diet_score = State()
    training_score = State()
    custom_score = State()


class EditGoalState(StatesGroup):
    init = State()
    create_new_goal_name = State()
    set_new_goal_value = State()
    edit_goal_value = State()
    edit_training_goal_type = State()
    edit_training_goal_type = State()
