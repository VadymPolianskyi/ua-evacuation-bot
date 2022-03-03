import logging

from aiogram.types import Message

from src.config import msg, marker
from src.db.entity import AnnouncementType
from src.handler.general import TelegramMessageHandler, MessageMeta, TelegramCallbackHandler, CallbackMeta
from src.service import markup
from src.service.announcement import AnnouncementService
from src.service.user import UserService


class MenuGeneral:

    def __init__(self, user_service: UserService, announcement_service: AnnouncementService):
        self.user_service = user_service
        self.announcement_service = announcement_service

    async def _show_menu(self, original_message: Message):
        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_BUTTON, marker.FIND, '_'),
            (msg.SHARE_BUTTON, marker.SHARE, '_'),
            (msg.MY_BUTTON, marker.MY, '_'),
            (msg.INFO_BUTTON, marker.INFO, '_')
        ])

        # users_today = self.user_service.count_last24_users()
        share_announcements_count = self.announcement_service.count_all()
        find_announcements_count = self.announcement_service.count_all(AnnouncementType.find)

        final_msg = msg.MENU.format(share_announcements_count, find_announcements_count)
        await original_message.answer(final_msg, reply_markup=menu_keyboard, disable_web_page_preview=True)


class MenuHandler(TelegramMessageHandler, MenuGeneral):
    def __init__(self, user_service: UserService, announcement_service: AnnouncementService):
        TelegramMessageHandler.__init__(self)
        MenuGeneral.__init__(self, user_service, announcement_service)

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"MenuHandler.handle for User({message.user_id})")
        await self._show_menu(message.original)


class MenuCallbackHandler(TelegramCallbackHandler, MenuGeneral):
    MARKER = marker.MENU

    def __init__(self, user_service: UserService, announcement_service: AnnouncementService):
        TelegramCallbackHandler.__init__(self)
        MenuGeneral.__init__(self, user_service, announcement_service)

    async def handle_(self, call: CallbackMeta):
        logging.info(f"MenuCallbackHandler.handle for User({call.user_id})")
        await self._show_menu(call.original.message)
