from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import ChatMemberUpdated
from app.database.db_service import DatabaseService


chat_router = Router()


# add user to DB when user join bot
@chat_router.my_chat_member(
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
@chat_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_left_bot_handler(
    chat_member_updated: ChatMemberUpdated,
    database: DatabaseService
) -> None:
    await database.delete_user(chat_member_updated.from_user.id)