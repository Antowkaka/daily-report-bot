from aiogram import Router, html, F
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import Message, ChatMemberUpdated

from app.database.db_service import DatabaseService

main_router = Router()


@main_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer('Hello')


# add user to DB when user join bot
@main_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_join_bot_handler(
    chat_member_updated: ChatMemberUpdated,
    database: DatabaseService
) -> None:
    await database.create_user(
        chat_member_updated.from_user.username,
        chat_member_updated.from_user.full_name,
        chat_member_updated.from_user.id,
    )


# remove user from DB when user left from bot
@main_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_left_bot_handler(
    chat_member_updated: ChatMemberUpdated,
    database: DatabaseService
) -> None:
    await database.delete_user(chat_member_updated.from_user.id)

