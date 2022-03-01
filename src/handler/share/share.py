from aiogram.types import Message

from src.config import marker, msg
from src.db.entity import AnnouncementType
from src.handler.general import TelegramCallbackHandler, CallbackMeta
from src.model import Announcement
from src.service import markup
from src.service.announcement import AnnouncementService
from src.service.city import CityService
import logging


class ShareGeneral:

    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        self.announcement_service = announcement_service
        self.city_service = city_service

    async def _show_share_menu(self, message: Message):
        menu_keyboard = markup.create_inline_markup_([
            (msg.SHARE_HOME_BUTTON, marker.SHARE_HOME, '_'),
            (msg.SHARE_TRIP_BUTTON, marker.SHARE_TRIP, '_'),
            (msg.BACK_BUTTON, marker.MENU, '_')
        ])

        await message.answer(msg.SHARE, reply_markup=menu_keyboard, disable_web_page_preview=True)

    async def _alert_if_match(self, message: Message, a: Announcement):
        logging.info(f"Alert if find subscriptions for {a.to_str()}")
        citi_to_id = a.city_to.id if a.city_to else None

        announcements_find = self.announcement_service.find_by_city(
            a.city_from.id, AnnouncementType.find, a.a_service, citi_to_id)
        users = [ann.user_id for ann in announcements_find]

        a_str = a.to_str()
        for user in users:
            await message.bot.send_message(user, msg.FOUND.format(a_str))


class ShareCallbackHandler(TelegramCallbackHandler, ShareGeneral):
    MARKER = marker.SHARE

    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        TelegramCallbackHandler.__init__(self)
        ShareGeneral.__init__(self, announcement_service, city_service)

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"ShareCallbackHandler.handle for User({callback.user_id})")
        await self._show_share_menu(callback.original.message)
