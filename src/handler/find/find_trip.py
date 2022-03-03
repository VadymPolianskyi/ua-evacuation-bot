import logging

from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.config import marker, msg
from src.db.entity import AnnouncementType, AnnouncementServiceType, City
from src.handler.find.find import FindGeneral
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.state import FindTripState
from src.service.announcement import AnnouncementService
from src.service.city import CityService


class FindTripGeneral:
    def __init__(self, city_service: CityService):
        self.city_service = city_service

    async def _show_cities(self, message: Message, tg_msg: str, with_any: bool = False):
        cities_buttons = [[KeyboardButton(tz)] for tz in self.city_service.find_all_titles(with_any=with_any)]
        await message.answer(
            tg_msg,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))


class FindTripCallbackHandler(TelegramCallbackHandler, FindTripGeneral):
    MARKER = marker.FIND_TRIP

    def __init__(self, city_service: CityService):
        TelegramCallbackHandler.__init__(self)
        FindTripGeneral.__init__(self, city_service)

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"FindTripCallbackHandler.handle for User({callback.user_id})")
        await self._show_cities(callback.original.message, msg.FIND_TRIP_CITY_FROM)
        await FindTripState.waiting_for_city_from.set()


class FindTripCityFromAnswerHandler(TelegramMessageHandler, FindTripGeneral):
    def __init__(self, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        FindTripGeneral.__init__(self, city_service)

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"FindTripCityFromAnswerHandler.handle for User({message.user_id})")
        city_from_name = message.text
        logging.debug(f"Input city FROM: {city_from_name}")
        city_from = self.city_service.find_by_name(city_from_name)

        if city_from and city_from.id != self.city_service.ANY_ID:
            await self._show_cities(message.original, msg.FIND_TRIP_CITY_TO, with_any=True)
            await FindTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)
        else:
            logging.info(f"Writing city FROM again for User({message.user_id})")
            await self._show_cities(message.original, msg.FIND_TRIP_CITY_FROM)
            await FindTripState.waiting_for_city_from.set()


class FindTripCityToAnswerHandler(TelegramMessageHandler, FindTripGeneral, FindGeneral):
    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        FindTripGeneral.__init__(self, city_service)
        FindGeneral.__init__(self, announcement_service)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"FindTripCityToAnswerHandler.handle for User({message.user_id})")

        city_from = (await Dispatcher.get_current().current_state().get_data())['city_from']
        city_to_name = message.text
        logging.debug(f"Input city TO: {city_to_name}")
        city_to: City = self.city_service.find_by_name(city_to_name)

        if city_to:
            res = self.announcement_service.find_by_city(
                city_from.id, AnnouncementType.share, AnnouncementServiceType.trip, city_to.id)

            announcements: str = "\n" + "\n\n".join([a.to_str() for a in res]) if res else msg.FIND_NOTHING

            final_message = msg.FIND_TRIP_RESULT.format(city_from.name, city_to.name, announcements).replace('_', '\_')
            await self._show_result(message.original, final_message)

            await Dispatcher.get_current().current_state().update_data(
                a_service=AnnouncementServiceType.trip, city_from=city_from, city_to=city_to)
        else:
            logging.info(f"Writing city TO again for User({message.user_id})")

            await self._show_cities(message.original, msg.FIND_TRIP_CITY_TO, with_any=True)
            await FindTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)
