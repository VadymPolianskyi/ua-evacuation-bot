from aiogram import Dispatcher
from aiogram.types import Message

from src.config import marker, msg
from src.db.entity import AnnouncementType
from src.handler.general import TelegramCallbackHandler, CallbackMeta
from src.service import markup
from src.service.announcement import AnnouncementService


class FindGeneral:

    def __init__(self, announcement_service: AnnouncementService):
        self.announcement_service = announcement_service

    async def _show_find_menu(self, message: Message, user_id: int):
        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_HOME_BUTTON, marker.FIND_HOME, '_'),
            (msg.FIND_TRIP_BUTTON, marker.FIND_TRIP, '_'),
            (msg.FIND_MY_BUTTON, marker.FIND_MY, '_'),
            (msg.BACK_BUTTON, marker.MENU, '_')
        ])

        before_text = ""
        user_announcements_find = self.announcement_service.find_by_user(user_id, AnnouncementType.find)
        if user_announcements_find:
            announcements_find_str = "\n".join(
                [f"{i + 1}. {a.to_str()}" for i, a in enumerate(user_announcements_find)])

            before_text = msg.FIND_BEFORE.format(announcements_find_str)

        await message.answer(before_text + msg.FIND, reply_markup=menu_keyboard, disable_web_page_preview=True)


class FindCallbackHandler(TelegramCallbackHandler, FindGeneral):
    MARKER = marker.FIND

    def __init__(self, announcement_service: AnnouncementService):
        TelegramCallbackHandler.__init__(self)
        FindGeneral.__init__(self, announcement_service)

    async def handle_(self, callback: CallbackMeta):
        await Dispatcher.get_current().current_state().finish()
        await self._show_find_menu(callback.original.message, callback.user_id)
