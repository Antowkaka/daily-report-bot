from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from app.database.db_service import DatabaseService
from app.entities.user import UserEntity
from app.text_config import get_text
from app.keyboards import first_step_keyboard, main_keyboard
from app.states import TrackDayState

main_router = Router()


@main_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, database: DatabaseService) -> None:
    user = await database.get_user(message.from_user.id)

    if user is not None:
        print(user)
        if user['goals'] is not None:
            existed_user_greeting_message = (
                f'{get_text('template-greeting-user-first-part')}'
                f' {message.from_user.full_name}, '
                f'{get_text('template-greeting-user-second-part-with-goals')}'
            )

            await state.update_data(user=user)
            await message.answer(existed_user_greeting_message, reply_markup=main_keyboard)
        else:
            existed_user_greeting_message = (
                f'{get_text('template-greeting-user-first-part')}'
                f' {message.from_user.full_name}, '
                f'{get_text('template-greeting-user-second-part-without-goals')}'
            )

            await message.answer(existed_user_greeting_message, reply_markup=first_step_keyboard)
    else:
        await message.answer(get_text('message-create-profile-before-next-actions'))


@main_router.message(Command('delete_profile'))
async def remove_profile_handler(message: Message, database: DatabaseService) -> None:
    user = await database.get_user(message.from_user.id)

    if user is None:
        await message.answer(get_text('message-profile-already-deleted'))
    else:
        await database.delete_user(message.from_user.id)
        await message.answer(get_text('message-profile-sucessfully-deleted'), reply_markup=ReplyKeyboardRemove())


@main_router.message(Command('create_profile'))
async def create_profile_handler(message: Message, database: DatabaseService) -> None:
    user = await database.get_user(message.from_user.id)

    if user is None:
        await database.create_user(UserEntity(message.from_user).model)
        await message.answer(get_text('message-profile-sucessfully-created'), reply_markup=first_step_keyboard)
    else:
        await message.answer(get_text('message-profile-already-created'))


@main_router.message(F.text == get_text('btn-track-your-day'))
async def track_day_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(get_text('message-track-diet'))


@main_router.message(F.text == get_text('btn-show-user-goals'))
async def show_goals_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Твої цілі')


@main_router.message(F.text == get_text('btn-statistic'))
async def show_goals_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Статистика поки не доступна')
