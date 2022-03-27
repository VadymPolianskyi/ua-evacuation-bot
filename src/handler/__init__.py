import json
import logging
from datetime import datetime
from json import JSONDecodeError

from aiogram.types import CallbackQuery
from aiogram.types import Message

from src.config import msg
from src.service import time_service


class MessageMeta:
    def __init__(self, message: Message, time: datetime):
        self.user_id = message.from_user.id
        self.text = message.text
        self.time = time
        self.original = message


class CallbackMeta:
    def __init__(self, call: CallbackQuery, time: datetime):
        self.user_id = call.from_user.id
        self.time = time
        try:
            self.payload = json.loads(call.data)
        except JSONDecodeError:
            self.payload = call.data
        self.original = call


class TelegramMessageHandler:

    def __init__(self):
        logging.debug(f'Creating {self.__class__.__name__}...')

    async def handle(self, message: Message, *args):
        user_id: int = message.from_user.id
        msg_time: datetime = time_service.now()
        logging.info(f"Message '{message.text}' in chat({user_id}) at '{msg_time}'. Args: {','.join(args)}")
        try:
            await self.handle_(MessageMeta(message, msg_time), *args)
        except Exception as e:
            logging.error(e)
            await message.answer(msg.ERROR_BASIC)

    async def handle_(self, message: MessageMeta, *args):
        """Response to Message"""
        pass


class TelegramCallbackHandler:
    def __init__(self):
        logging.debug(f'Creating {self.__class__.__name__}...')

    async def handle(self, call: CallbackQuery):
        user_id: int = call.from_user.id
        callback_time: datetime = time_service.now()
        logging.info(f"Callback with data '{call.data}' in chat({user_id}) at '{callback_time}'")
        try:
            await call.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
            await self.handle_(CallbackMeta(call, time=callback_time))
        except Exception as e:
            logging.error(e)
            await call.message.answer(msg.ERROR_BASIC)

    async def handle_(self, call: CallbackMeta):
        """Response to Callback Message"""
        pass
