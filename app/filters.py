from aiogram.types import Message
from aiogram.filters import Filter

from app.text_config import get_text


class FilterGoalValue(Filter):
    async def __call__(self, msg: Message) -> bool:
        try:
            int(msg.text)
            return True
        except ValueError:
            await msg.answer(get_text('message-value-format-error'))
            return False


class FilterTextMessage(Filter):
    async def __call__(self, msg: Message) -> bool:
        if msg.text:
            return True
        else:
            await msg.answer(get_text('message-value-not-a-text-error'))
            return False
