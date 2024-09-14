import asyncio
import logging
import sys
from typing import List
from os import getenv

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.database.db_service import DatabaseService
from app.routers.chat_router import chat_router
from app.routers.goals_setting_router import goals_setting_router
from app.routers.main_router import main_router

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()

commands: List[BotCommand] = [
    BotCommand(command='/start', description='Запустити бота'),
    BotCommand(command='/create_profile', description='Створити профіль'),
    BotCommand(command='/delete_profile', description='Видалити профіль'),
]


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())

    dp.include_routers(chat_router, main_router, goals_setting_router)

    # And the run events dispatching
    await dp.start_polling(bot, database=DatabaseService())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
