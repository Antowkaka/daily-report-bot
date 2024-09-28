import pprint

from aiogram import Router, F, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.db_service import DatabaseService
from app.entities.user import UserEntity
from app.entities.goal import GoalEntity, GoalChangeAccessType
from app.text_config import get_text
from app.states import TrackDayState, EditGoalState
from app.callback_dates import EditGoalCallbackData, EditTrainingTypeGoalCallbackData
from app.filters import FilterTextMessage, FilterGoalValue
from app.utils import out_time_tracking, prepare_statistic_data

import app.keyboards as k_boards

main_router = Router()


@main_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    user = await database.get_user(message.from_user.id)

    if user is not None:
        await state.clear()
        await state.update_data(user=user)
        if user['goals'] is not None:
            await message.answer(get_text('message-main-menu'), reply_markup=k_boards.main_keyboard)
        else:
            existed_user_greeting_message = (
                f'{get_text('template-greeting-user-first-part')}'
                f' {message.from_user.full_name}, '
                f'{get_text('template-greeting-user-second-part-without-goals')}'
            )

            await message.answer(existed_user_greeting_message, reply_markup=k_boards.first_step_keyboard)
    else:
        await message.answer(get_text('message-create-profile-before-next-actions'))


@main_router.message(Command('delete_profile'))
async def remove_profile_handler(message: Message, database: DatabaseService) -> None:
    user = await database.get_user(message.from_user.id)

    if user is None:
        await message.answer(get_text('message-profile-already-deleted'))
    else:
        await database.delete_user(message.from_user.id)
        await database.delete_all_reports(message.from_user.id)
        await message.answer(get_text('message-profile-sucessfully-deleted'), reply_markup=ReplyKeyboardRemove())


@main_router.message(Command('create_profile'))
async def create_profile_handler(message: Message, database: DatabaseService) -> None:
    user = await database.get_user(message.from_user.id)

    if user is None:
        await database.create_user(UserEntity(message.from_user).model)
        await message.answer(get_text('message-profile-sucessfully-created'), reply_markup=k_boards.first_step_keyboard)
    else:
        await message.answer(get_text('message-profile-already-created'))


@main_router.message(F.text == get_text('btn-main-keyboard-track-your-day'))
async def track_day_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    # get last report and check date
    last_report = await database.get_last_report()
    out_of_tracking_message = out_time_tracking(last_report)

    # check is available to track
    if out_of_tracking_message is None:
        await state.set_state(TrackDayState.diet_score)
        await message.answer(get_text('message-track-diet'), reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(out_of_tracking_message, reply_markup=k_boards.main_keyboard)


@main_router.message(F.text == get_text('btn-main-keyboard-show-user-goals'))
async def show_goals_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(EditGoalState.init)
    await message.answer(
        get_text('message-goal-menu'),
        reply_markup=k_boards.create_goals_keyboard(data['user']['goals'])
    )


@main_router.callback_query(EditGoalState.init, EditGoalCallbackData.filter())
async def edit_goal_main_handler(
        callback: CallbackQuery,
        callback_data: EditGoalCallbackData,
        state: FSMContext
) -> None:
    if callback_data.name:
        await state.update_data({
            'goal_key': callback_data.key,
            'goal_name': callback_data.name
        })

        await callback.message.delete()

        # branch for updating training type goal
        if callback_data.name == get_text('goal-name-training-type'):
            data = await state.get_data()
            await state.set_state(EditGoalState.edit_training_goal_type)
            await callback.answer()

            change_training_type_text = (
                f'{get_text('template-change-goal')} "{callback_data.name}"'
                f'\n{html.bold(get_text('message-goal-available-training-types'))}'
            )
            await callback.message.answer(
                change_training_type_text,
                reply_markup=k_boards.create_available_training_types_keyboard(
                    data['user']['goals'][callback_data.key]['goalValue']
                )
            )
        else:
            await callback.answer()
            await callback.message.answer(
                f'{get_text('template-change-goal')} "{callback_data.name}":',
                reply_markup=k_boards.create_goal_menu_keyboard(callback_data.is_deletable)
            )
    # branch for creating new goal
    else:
        await state.update_data(goal_key=callback_data.key)
        await state.set_state(EditGoalState.create_new_goal_name)

        await callback.message.delete()
        await callback.answer()
        await callback.message.answer(get_text('message-set-custom-goal-suggestion'))


# Start CRUD methods
# CREATE
@main_router.message(EditGoalState.create_new_goal_name, FilterTextMessage())
async def create_new_goal_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(goal_name=message.text)
    await state.set_state(EditGoalState.set_new_goal_value)

    await message.answer(f'{get_text('template-set-custom-goal')} "{message.text}":')


@main_router.message(EditGoalState.set_new_goal_value, FilterTextMessage(), FilterGoalValue())
async def set_new_goal_value_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    data = await state.get_data()
    await state.clear()

    goal = GoalEntity({
        'name': data['goal_name'],
        'value': int(message.text),
        'change_access': GoalChangeAccessType.deletable.value
    })
    user_with_new_goal = await database.add_new_user_goal(message.from_user.id, data['goal_key'], goal.model)

    await state.update_data(user=user_with_new_goal)
    await message.answer(get_text('message-goal-new-value-created'), reply_markup=k_boards.main_keyboard)


# UPDATE
@main_router.message(EditGoalState.init, F.text == get_text('btn-edit-goal-keyboard-edit-value'))
async def edit_goal_value_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(EditGoalState.edit_goal_value)

    await message.answer(get_text('message-goal-input-new-value'))


@main_router.callback_query(EditGoalState.edit_training_goal_type, EditTrainingTypeGoalCallbackData.filter())
async def edit_training_type_goal_handler(
        callback: CallbackQuery,
        callback_data: EditTrainingTypeGoalCallbackData,
        state: FSMContext,
        database: DatabaseService
) -> None:
    await database.update_user_training_type_goal(callback.from_user.id, callback_data.type)

    await state.update_data(goal_key='trainingGoal')
    await state.set_state(EditGoalState.edit_goal_value)
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(get_text('message-goal-input-new-value'))


@main_router.message(EditGoalState.edit_goal_value, FilterTextMessage(), FilterGoalValue())
async def set_goal_value_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    data = await state.get_data()
    await state.clear()
    updated_user = await database.update_user_goal(message.from_user.id, data['goal_key'], int(message.text))

    await state.update_data(user=updated_user)
    await message.answer(get_text('message-goal-new-value-settled'), reply_markup=k_boards.main_keyboard)


# DELETE
@main_router.message(EditGoalState.init, F.text == get_text('btn-edit-goal-keyboard-delete-goal'))
async def delete_goal_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    data = await state.get_data()
    await state.clear()
    updated_user = await database.delete_user_goal(message.from_user.id, data['goal_key'])

    await state.update_data(user=updated_user)
    await message.answer(get_text('message-goal-deleted'), reply_markup=k_boards.main_keyboard)


# end CRUD methods


@main_router.message(EditGoalState.init, F.text == get_text('btn-edit-goal-keyboard-go-back'))
async def edit_goal_go_back_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data({
        'goal_key': None,
        'goal_name': None
    })

    await message.answer(
        get_text('message-goal-menu'),
        reply_markup=k_boards.create_goals_keyboard(data['user']['goals'])
    )


@main_router.message(F.text == get_text('btn-main-keyboard-statistic'))
async def statistic_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    reports, remaining_days = await database.get_last_week_reports()

    if remaining_days:
        await message.answer(
            f'{get_text('message-db-week-not-full')} {remaining_days}',
            reply_markup=k_boards.main_keyboard
        )
    else:
        await message.answer(
            get_text('message-statistic-type'),
            reply_markup=k_boards.statistic_keyboard
        )


@main_router.message(F.text == get_text('btn-statistic-keyboard-text'))
async def statistic_text_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    await message.answer('Text statistic')


@main_router.message(F.text == get_text('btn-statistic-keyboard-charts'))
async def statistic_charts_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    await message.answer('Charts statistic')
