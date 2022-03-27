import logging

from aiogram import Dispatcher
from aiogram.types import Message

from src.config import marker, msg, limits
from src.db.entity import AnnouncementType
from src.handler import TelegramCallbackHandler, CallbackMeta
from src.service import markup
from src.service.announcement import AnnouncementService
from src.service.message_separator import separate


class FindGeneral:

    def __init__(self, announcement_service: AnnouncementService):
        self.announcement_service = announcement_service

    async def _show_find_menu(self, message: Message, user_id: int):
        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_HOME_BUTTON, marker.FIND_HOME, '_'),
            (msg.FIND_TRIP_BUTTON, marker.FIND_TRIP, '_'),
            (msg.FIND_HELP_BUTTON, marker.FIND_HELP, '_'),
            (msg.FIND_MY_BUTTON, marker.FIND_MY, '_'),
            (msg.BLACK_LIST_BUTTON, marker.BLACK_LIST, '_'),
            (msg.BACK_BUTTON, marker.MENU, '_')
        ])

        before_text = ""
        user_announcements_find = self.announcement_service.find_by_user(user_id, AnnouncementType.find)
        if user_announcements_find:
            announcements_find_str = "\n".join(
                [f"{i + 1}. {a.to_str()}" for i, a in enumerate(user_announcements_find)])

            before_text = msg.FIND_BEFORE.format(announcements_find_str)
        logging.info(f"Before text: {before_text}")
        await message.answer(before_text + msg.FIND, reply_markup=menu_keyboard, disable_web_page_preview=True)

    async def _show_result(self, message: Message, final_message: str):
        logging.info(f"Find Final message: {final_message}")

        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_CREATE_BUTTON, marker.FIND_CREATE, '_'),
            (msg.BACK_BUTTON, marker.FIND, '_')
        ])

        if len(final_message) > limits.FIND_RESPONSE_LIMIT:
            logging.info(f"Response more messages becaulse of text length = {len(final_message)}")
            separated = separate(final_message)
            for m in separated:
                if separated.index(m) == len(separated) - 1 and len(m) > 0:
                    await message.answer(m, reply_markup=menu_keyboard, disable_web_page_preview=True)
                else:
                    await message.answer(m, disable_web_page_preview=True)
        else:
            await message.answer(final_message, reply_markup=menu_keyboard, disable_web_page_preview=True)


class FindCallbackHandler(TelegramCallbackHandler, FindGeneral):
    MARKER = marker.FIND

    def __init__(self, announcement_service: AnnouncementService):
        TelegramCallbackHandler.__init__(self)
        FindGeneral.__init__(self, announcement_service)

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"FindCallbackHandler.handle for User({callback.user_id})")
        await Dispatcher.get_current().current_state().finish()
        await self._show_find_menu(callback.original.message, callback.user_id)
