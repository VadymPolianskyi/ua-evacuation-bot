from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.config import marker, msg
from src.config.limits import INFO_SYMBOLS_LIMIT
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.share.share import ShareGeneral
from src.handler.state import ShareHomeState
from src.service import cities
from src.service.announcement import AnnouncementService


class ShareHomeGeneral:
    async def _show_cities(self, message: Message):
        cities_buttons = [[KeyboardButton(tz)] for tz in cities.all()]

        await message.answer(
            msg.SHARE_HOME_CITY,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))
        await ShareHomeState.waiting_for_city.set()


class ShareHomeCallbackHandler(TelegramCallbackHandler, ShareHomeGeneral):
    MARKER = marker.SHARE_HOME

    def __init__(self):
        TelegramCallbackHandler.__init__(self)
        ShareHomeGeneral.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        await self._show_cities(callback.original.message)


class ShareHomePostCityAnswerHandler(TelegramMessageHandler, ShareHomeGeneral):
    def __init__(self, ):
        TelegramMessageHandler.__init__(self)
        ShareHomeGeneral.__init__(self)

    async def handle_(self, message: MessageMeta, *args):
        city = message.text

        if cities.validate(city):

            await message.original.answer(msg.SHARE_HOME_INFO)
            await ShareHomeState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city=city)
        else:
            await self._show_cities(message.original)


class ShareHomePostInfoAnswerHandler(TelegramMessageHandler, ShareGeneral):
    def __init__(self, announcement_service: AnnouncementService):
        TelegramMessageHandler.__init__(self)
        ShareGeneral.__init__(self)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        info = message.text
        city = (await Dispatcher.get_current().current_state().get_data())['city']

        if len(info) <= INFO_SYMBOLS_LIMIT:
            self.announcement_service.create_home(message.user_id, AnnouncementType.share,
                                                  AnnouncementServiceType.home, city, info)
            # todo: find all for this city and send them
            await message.original.answer(msg.SHARE_HOME_DONE.format(city, info))
            await Dispatcher.get_current().current_state().finish()
            await self._show_share_menu(message.original)
        else:
            diff = len(info) - INFO_SYMBOLS_LIMIT

            await message.original.answer(msg.SHARE_INFO_WARNING.format(diff) + "\n" + msg.SHARE_HOME_INFO)
            await ShareHomeState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city=city)
