from typing import Dict, Any
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database.db_service import DatabaseService
from app.states import SetGoalsState
from app.filters import FilterGoalValue
from app.text_config import get_text
from app.callback_dates import TrainingTypeCallbackData, SkipStepCallbackData, CompleteCallbackData
from app.utils import convert_goals_row_dict_to_db_goals
from app.types import TrainingGoalType, SkipStepType, CompleteStepType

import app.keyboards as k_boards

goals_setting_router = Router()


# set diet goal flow
@goals_setting_router.message(F.text == get_text('btn-set-goals'))
async def set_diet_goal_first_step_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(SetGoalsState.diet_goal)
    await message.answer(get_text('message-set-diet-goal'))


@goals_setting_router.message(SetGoalsState.diet_goal, FilterGoalValue())
async def set_diet_goal_second_step_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(diet_goal=int(message.text))

    await state.set_state(SetGoalsState.training_goal)
    training_goal_answer = f'''
        {get_text('message-set-training-goal')}
        {get_text('message-set-training-goal-option-1')}
        {get_text('message-set-training-goal-option-2')}
    '''
    await message.answer(training_goal_answer, reply_markup=k_boards.training_goal_types_keyboard)


# set training goal flow
@goals_setting_router.callback_query(SetGoalsState.training_goal, TrainingTypeCallbackData.filter())
async def set_training_goal_type_handler(
    callback: CallbackQuery,
    callback_data: TrainingTypeCallbackData,
    state: FSMContext
) -> None:
    await state.update_data(training_goal_type=callback_data.goal_type.value)
    await state.set_state(SetGoalsState.training_goal_type)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    match callback_data.goal_type:
        case TrainingGoalType.trainings_per_week:
            await callback.message.answer(get_text('message-set-training-goal-option-1-wait-input'))
        case TrainingGoalType.trainings_kcal:
            await callback.message.answer(get_text('message-set-training-goal-option-2-wait-input'))


@goals_setting_router.message(SetGoalsState.training_goal_type, FilterGoalValue())
async def set_training_goal_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(training_goal=int(message.text))

    await state.set_state(SetGoalsState.sleep_goal)
    await message.answer(get_text('message-set-sleep-goal'))


# set sleep goal flow
@goals_setting_router.message(SetGoalsState.sleep_goal, FilterGoalValue())
async def set_sleep_goal_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(sleep_goal=int(message.text))

    await state.set_state(SetGoalsState.custom_goal_name)
    await state.update_data(temp_iterator=1)
    await message.answer(
        get_text('message-set-custom-goal-suggestion'),
        reply_markup=k_boards.set_custom_goal_skip_keyboard
    )


# set custom goal name flow
@goals_setting_router.message(SetGoalsState.custom_goal_name)
async def set_custom_goal_name_handler(message: Message, state: FSMContext) -> None:
    # 1. get data for iteration custom goals
    data = await state.get_data()
    temp_iterator = data['temp_iterator']

    # 2. set custom goal name
    await state.update_data({f'custom_goal_{temp_iterator}': {'name': message.text, 'goal': None}})
    # 3. iterate value
    await state.update_data(temp_iterator=temp_iterator + 1)

    # 4. suggest next goal
    await message.answer(
        get_text('message-set-next-custom-goal'),
        reply_markup=k_boards.set_custom_goal_complete_keyboard
    )


# handle skip custom goal setting
@goals_setting_router.callback_query(
    SetGoalsState.custom_goal_name,
    SkipStepCallbackData.filter(F.step == SkipStepType.skip_custom_goal_setting)
)
async def skip_custom_goal_settinge_handler(
    callback: CallbackQuery,
    state: FSMContext,
    database: DatabaseService
) -> None:
    # 1. convert goals state to db goals object
    raw_final_goals = await state.get_data()
    db_goals = convert_goals_row_dict_to_db_goals(raw_final_goals)

    # 2. setting goals to db and clean up state
    await database.update_user_goals(callback.from_user.id, db_goals)
    await state.clear()

    # 3. handle previous message and answer
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer(get_text('message-setting-goals-completed'))


def create_text_for_custom_goal(data: Dict[str, Any], iterator: int) -> str:
    return f'{get_text("template-set-custom-goal")} {data[f"custom_goal_{iterator}"]['name']:}'


# handle complete custom goal setting
@goals_setting_router.callback_query(
    SetGoalsState.custom_goal_name,
    CompleteCallbackData.filter(F.step == CompleteStepType.complete_custom_goal_setting)
)
async def complete_custom_goal_settinge_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    # 1. get data for creating message
    data = await state.get_data()

    await state.set_state(SetGoalsState.custom_goal)
    await state.update_data(temp_iterator=1)
    await callback.answer()

    await callback.message.answer(create_text_for_custom_goal(data, 1))


# set custom goal flow
@goals_setting_router.message(SetGoalsState.custom_goal, FilterGoalValue())
async def set_custom_goal_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    # 1. get data for iteration custom goals
    data = await state.get_data()
    temp_iterator = data['temp_iterator']
    custom_goal_key = f'custom_goal_{temp_iterator}'

    # 2. check count of custom goals
    data_keys_as_list = list(data.keys())
    filtered_data_keys = filter(lambda x: re.search('custom_goal', x), data_keys_as_list)
    goals_count = len(list(filtered_data_keys))

    if temp_iterator == goals_count:
        # 3a. update last goal
        await state.update_data({custom_goal_key: {'name': data[custom_goal_key]['name'], 'goal': message.text}})

        # 1. convert goals state to db goals object
        raw_final_goals = await state.get_data()
        db_goals = convert_goals_row_dict_to_db_goals(raw_final_goals)

        # 2. setting goals to db and clean up state
        await database.update_user_goals(message.from_user.id, db_goals)
        await state.clear()

        # 3. answer
        await message.answer(get_text('message-setting-goals-completed'))
    else:
        # 3b. create next iterator
        next_goal_index = temp_iterator + 1
        # 4b. set current goal
        await state.update_data({custom_goal_key: {'name': data[custom_goal_key]['name'], 'goal': message.text}})
        # 5b. iterate value
        await state.update_data(temp_iterator=next_goal_index)
        # 6b. suggest next goal
        await message.answer(create_text_for_custom_goal(data, next_goal_index))
