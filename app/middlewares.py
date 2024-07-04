import asyncio
from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject
# from aiogram.dispatcher.handler import CancelHandler
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int, interval: int):
        self.limit = limit
        self.interval = interval
        self.users = defaultdict(list)

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        now = datetime.now()

        # Filter out outdated timestamps
        self.users[user_id] = [timestamp for timestamp in self.users[user_id] if
                               now - timestamp < timedelta(seconds=self.interval)]

        # Check the number of messages sent in the interval
        if len(self.users[user_id]) >= self.limit:
            await event.answer("Too many requests, please slow down.")
            # raise CancelHandler()

        # Add the current timestamp
        self.users[user_id].append(now)

        result = await handler(event, data)
        return result
