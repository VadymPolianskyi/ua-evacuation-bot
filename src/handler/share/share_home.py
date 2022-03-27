import logging

from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.config import marker, msg
from src.config.limits import INFO_SYMBOLS_LIMIT
from src.db.entity import AnnouncementType, AnnouncementServiceType, City
from src.handler import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.share.share import ShareGeneral
from src.handler.state import ShareHomeState
from src.service.announcement import AnnouncementService
from src.service.city import CityService


class ShareHomeGeneral:

    def __init__(self, city_service: CityService):
        self.city_service = city_service

    async def _show_cities(self, message: Message):
        cities_buttons = [[KeyboardButton(tz)] for tz in self.city_service.find_all_titles()]

        await message.answer(
            msg.SHARE_HOME_CITY,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))
        await ShareHomeState.waiting_for_city.set()


class ShareHomeCallbackHandler(TelegramCallbackHandler, ShareHomeGeneral):
    MARKER = marker.SHARE_HOME

    def __init__(self, city_service: CityService):
        TelegramCallbackHandler.__init__(self)
        ShareHomeGeneral.__init__(self, city_service)

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"ShareHomeCallbackHandler.handle for User({callback.user_id})")
        await self._show_cities(callback.original.message)


class ShareHomePostCityAnswerHandler(TelegramMessageHandler, ShareHomeGeneral):
    def __init__(self, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        ShareHomeGeneral.__init__(self, city_service)

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"ShareHomePostCityAnswerHandler.handle for User({message.user_id})")
        city_name = message.text
        logging.debug(f"Input city: {city_name}")
        city: City = self.city_service.find_by_name(city_name)

        if city:

            await message.original.answer(msg.SHARE_HOME_INFO, reply_markup=ReplyKeyboardRemove())
            await ShareHomeState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city=city)
        else:
            await self._show_cities(message.original)


class ShareHomePostInfoAnswerHandler(TelegramMessageHandler, ShareGeneral):
    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        ShareGeneral.__init__(self, announcement_service, city_service)

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"ShareHomePostInfoAnswerHandler.handle for User({message.user_id})")
        info = message.text
        city: City = (await Dispatcher.get_current().current_state().get_data())['city']

        if len(info) <= INFO_SYMBOLS_LIMIT:
            ae = self.announcement_service.create(
                user_id=message.user_id,
                a_type=AnnouncementType.share,
                a_service=AnnouncementServiceType.home,
                city_from_id=city.id,
                info=info)

            await message.original.answer(msg.SHARE_HOME_DONE.format(city.name, info))
            await Dispatcher.get_current().current_state().finish()
            await self._alert_if_match(message.original, ae)
            await self._show_share_menu(message.original)
        else:
            diff = len(info) - INFO_SYMBOLS_LIMIT

            await message.original.answer(msg.SHARE_INFO_WARNING.format(diff) + "\n" + msg.SHARE_HOME_INFO)
            await ShareHomeState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city=city)
