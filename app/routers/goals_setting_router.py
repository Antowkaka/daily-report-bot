from typing import Dict, Any
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database.db_service import DatabaseService
from app.states import SetGoalsState
from app.filters import FilterGoalValue, FilterTextMessage
from app.text_config import get_text
from app.callback_dates import TrainingTypeCallbackData, SkipStepCallbackData, CompleteCallbackData
from app.entities.goal import GoalEntity, GoalChangeAccessType
from app.types import TrainingGoalType, SkipStepType, CompleteStepType

import app.keyboards as k_boards

goals_setting_router = Router()


# set diet goal flow
@goals_setting_router.message(F.text == get_text('btn-greeting-keyboard-set-goals'))
async def set_diet_goal_first_step_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(SetGoalsState.diet_goal)
    await message.answer(get_text('message-set-diet-goal'))


@goals_setting_router.message(SetGoalsState.diet_goal, FilterTextMessage(), FilterGoalValue())
async def set_diet_goal_second_step_handler(message: Message, state: FSMContext) -> None:
    await state.update_data({'dietGoal': GoalEntity({
        'name': 'їжа',
        'value': int(message.text),
        'change_access': GoalChangeAccessType.editable.value
    }).model})

    await state.set_state(SetGoalsState.training_goal)
    await message.answer(get_text('message-set-training-goal'), reply_markup=k_boards.training_goal_types_keyboard)


# set training goal flow
@goals_setting_router.callback_query(SetGoalsState.training_goal, TrainingTypeCallbackData.filter())
async def set_training_goal_type_handler(
    callback: CallbackQuery,
    callback_data: TrainingTypeCallbackData,
    state: FSMContext
) -> None:
    await state.update_data({'trainingGoalType': GoalEntity({
        'name': get_text('goal-name-training-type'),
        'value': callback_data.goal_type.value,
        'change_access': GoalChangeAccessType.editable.value
    }).model})
    await state.set_state(SetGoalsState.training_goal_type)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    match callback_data.goal_type:
        case TrainingGoalType.trainings_per_week:
            await callback.message.answer(get_text('message-set-training-goal-option-1-wait-input'))
        case TrainingGoalType.trainings_kcal:
            await callback.message.answer(get_text('message-set-training-goal-option-2-wait-input'))


@goals_setting_router.message(SetGoalsState.training_goal_type, FilterTextMessage(), FilterGoalValue())
async def set_training_goal_handler(message: Message, state: FSMContext) -> None:
    await state.update_data({'trainingGoal': GoalEntity({
        'name': 'тренування',
        'value': int(message.text),
        'change_access': GoalChangeAccessType.editable.value
    }).model})

    await state.set_state(SetGoalsState.sleep_goal)
    await message.answer(get_text('message-set-sleep-goal'))


# set sleep goal flow
@goals_setting_router.message(SetGoalsState.sleep_goal, FilterTextMessage(), FilterGoalValue())
async def set_sleep_goal_handler(message: Message, state: FSMContext) -> None:
    await state.update_data({'sleepGoal': GoalEntity({
        'name': 'сон',
        'value': int(message.text),
        'change_access': GoalChangeAccessType.editable.value
    }).model})

    await state.set_state(SetGoalsState.custom_goal_name)
    await state.update_data(temp_iterator=1)
    await message.answer(
        get_text('message-set-custom-goal-suggestion'),
        reply_markup=k_boards.set_custom_goal_skip_keyboard
    )


# set custom goal name flow
@goals_setting_router.message(SetGoalsState.custom_goal_name, FilterTextMessage())
async def set_custom_goal_name_handler(message: Message, state: FSMContext) -> None:
    if message.text:
        # 1. get data for iteration custom goals
        data = await state.get_data()
        temp_iterator = data['temp_iterator']

        # 2. set custom goal name BUT AS CLASS for future changes
        await state.update_data({f'customGoal_{temp_iterator}': GoalEntity({
            'name': message.text,
            'value': None,
            'change_access': GoalChangeAccessType.deletable.value
        })})
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
    final_goals = await state.get_data()
    del final_goals['temp_iterator']
    del final_goals['user']

    # 2. setting goals to db and clean up state
    await database.set_user_goals(callback.from_user.id, final_goals)
    await state.clear()

    # 3. set user for main menu interactions
    user = await database.get_user(callback.from_user.id)
    await state.update_data(user=user)

    # 4. handle previous message and answer
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer(get_text('message-setting-goals-completed'), reply_markup=k_boards.main_keyboard)


def create_text_for_custom_goal(data: Dict[str, GoalEntity], iterator: int) -> str:
    return f'{get_text("template-set-custom-goal")} {data[f"customGoal_{iterator}"].name:}'


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
@goals_setting_router.message(SetGoalsState.custom_goal, FilterTextMessage(), FilterGoalValue())
async def set_custom_goal_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    # 1. update value
    data = await state.get_data()
    temp_iterator = data['temp_iterator']
    custom_goal_key = f'customGoal_{temp_iterator}'
    goal_entity: GoalEntity = data[custom_goal_key]
    goal_entity.update_value(int(message.text))
    # Note. Convert class to model
    await state.update_data({custom_goal_key: goal_entity.model})

    # 2. check count of custom goals
    data_keys_as_list = list(data.keys())
    filtered_data_keys = filter(lambda x: re.search('customGoal', x), data_keys_as_list)
    goals_count = len(list(filtered_data_keys))

    if temp_iterator == goals_count:
        # 1. convert goals state to db goals object
        final_goals = await state.get_data()
        del final_goals['temp_iterator']
        del final_goals['user']

        # 2. setting goals to db and clean up state
        await database.set_user_goals(message.from_user.id, final_goals)
        await state.clear()

        # 3. set user for main menu interactions
        user = await database.get_user(message.from_user.id)
        await state.update_data(user=user)

        # 4. answer
        await message.answer(get_text('message-setting-goals-completed'), reply_markup=k_boards.main_keyboard)
    else:
        # 3b. create next iterator
        next_goal_index = temp_iterator + 1
        # 4b. iterate value
        await state.update_data(temp_iterator=next_goal_index)
        # 5b. suggest next goal
        await message.answer(create_text_for_custom_goal(data, next_goal_index))
