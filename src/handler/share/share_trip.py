import logging
from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.config import marker, msg
from src.config.limits import INFO_SYMBOLS_LIMIT
from src.config.msg import SHARE_INFO_WARNING
from src.db.entity import AnnouncementType, AnnouncementServiceType, City
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.share.share import ShareGeneral
from src.handler.state import ShareTripState
from src.service import time_service, markup
from src.service.announcement import AnnouncementService
from src.service.city import CityService


class ShareTripGeneral:

    def __init__(self, city_service: CityService):
        self.city_service = city_service

    async def _show_cities(self, message: Message, tg_msg: str,
                           except_city_id: str = None,
                           with_any: bool = False):
        logging.info("Create Cities Buttons")
        cities_buttons = [[KeyboardButton(c)] for c in self.city_service.find_all_titles(except_city_id, with_any)]
        await message.answer(
            tg_msg,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))


class ShareTripCallbackHandler(TelegramCallbackHandler, ShareTripGeneral):
    MARKER = marker.SHARE_TRIP

    def __init__(self, city_service: CityService):
        TelegramCallbackHandler.__init__(self)
        ShareTripGeneral.__init__(self, city_service)

    async def handle_(self, callback: CallbackMeta):
        await self._show_cities(callback.original.message, msg.SHARE_TRIP_CITY_FROM)
        await ShareTripState.waiting_for_city_from.set()


# city from
class ShareTripCityFromAnswerHandler(TelegramMessageHandler, ShareTripGeneral):
    def __init__(self, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        ShareTripGeneral.__init__(self, city_service)

    async def handle_(self, message: MessageMeta, *args):
        city_from_name = message.text
        logging.debug(f"Input city FROM: {city_from_name}")
        city_from: City = self.city_service.find_by_name(city_from_name)

        if city_from:
            await self._show_cities(message.original, msg.SHARE_TRIP_CITY_TO,
                                    except_city_id=city_from.id,
                                    with_any=True)
            await ShareTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)
        else:
            logging.info(f"Writing city FROM again for User({message.user_id})")
            await self._show_cities(message.original, msg.SHARE_TRIP_CITY_FROM)
            await ShareTripState.waiting_for_city_from.set()


# city to
class ShareTripCityToAnswerHandler(TelegramMessageHandler, ShareTripGeneral):
    def __init__(self, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        ShareTripGeneral.__init__(self, city_service)

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"ShareTripCityToAnswerHandler.handle for User({message.user_id})")
        city_from: City = (await Dispatcher.get_current().current_state().get_data())['city_from']
        city_to_name = message.text
        logging.debug(f"Input city FROM: {city_to_name}")
        city_to: City = self.city_service.find_by_name(city_to_name)

        if city_to:
            keyboard = markup.create_inline_markup_([(msg.SHARE_TRIP_REGULAR_BUTTON, marker.SHARE_TRIP_REGULAR, '_')])

            await message.original.answer(msg.SHARE_TRIP_SCHEDULING, reply_markup=keyboard)
            await ShareTripState.waiting_for_scheduling.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to)
        else:
            logging.info(f"Writing city TO again for User({message.user_id})")
            await self._show_cities(message.original, msg.SHARE_TRIP_CITY_TO,
                                    except_city_id=city_from.id,
                                    with_any=True)
            await ShareTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)


# scheduling callback
class ShareTripSchedulingAnswerCallbackHandler(TelegramCallbackHandler):
    MARKER = marker.SHARE_TRIP_REGULAR

    def __init__(self):
        TelegramCallbackHandler.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"ShareTripSchedulingAnswerCallbackHandler.handle for User({callback.user_id})")
        state_data: dict = await Dispatcher.get_current().current_state().get_data()
        city_from: City = state_data['city_from']
        city_to: City = state_data['city_to']

        await callback.original.message.answer(msg.SHARE_TRIP_INFO)
        await ShareTripState.waiting_for_info.set()
        await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to)


# scheduling
class ShareTripSchedulingAnswerHandler(TelegramMessageHandler, ShareTripGeneral):
    def __init__(self, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        ShareTripGeneral.__init__(self, city_service)

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"ShareTripSchedulingAnswerHandler.handle for User({message.user_id})")
        state_data: dict = await Dispatcher.get_current().current_state().get_data()
        city_from: City = state_data['city_from']
        city_to: City = state_data['city_to']
        scheduling = message.text
        logging.debug(f"Input scheduling: {scheduling}")

        extracted_schedule: datetime = time_service.extract_datetime(scheduling)

        if extracted_schedule:
            await message.original.answer(msg.SHARE_TRIP_INFO)
            await ShareTripState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to,
                                                                       scheduling=extracted_schedule)
        else:
            logging.info(f"Writing scheduling again for User({message.user_id})")
            keyboard = markup.create_inline_markup_([(msg.SHARE_TRIP_REGULAR_BUTTON, marker.SHARE_TRIP_REGULAR, '_')])

            await message.original.answer(msg.SHARE_TRIP_SCHEDULING, reply_markup=keyboard)
            await ShareTripState.waiting_for_scheduling.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to)


class ShareTripInfoAnswerHandler(TelegramMessageHandler, ShareGeneral):
    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        ShareGeneral.__init__(self, announcement_service, city_service)

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"ShareTripInfoAnswerHandler.handle for User({message.user_id})")
        state_data: dict = await Dispatcher.get_current().current_state().get_data()
        city_from: City = state_data['city_from']
        city_to: City = state_data['city_to']
        scheduled: datetime = state_data['scheduling'] if 'scheduling' in state_data.keys() else None

        info = message.text

        if len(info) <= INFO_SYMBOLS_LIMIT:
            a = self.announcement_service.create(
                user_id=message.user_id,
                a_type=AnnouncementType.share,
                a_service=AnnouncementServiceType.trip,
                city_from_id=city_from.id,
                city_to_id=city_to.id,
                info=info,
                scheduled=scheduled)

            await message.original.answer(msg.SHARE_TRIP_DONE.format(city_from.name, city_to.name))
            await Dispatcher.get_current().current_state().finish()
            await self._alert_if_match(message.original, a)
            await self._show_share_menu(message.original)
        else:
            diff = len(info) - INFO_SYMBOLS_LIMIT

            await message.original.answer(SHARE_INFO_WARNING.format(diff) + "\n" + msg.SHARE_TRIP_INFO)
            await ShareTripState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to,
                                                                       scheduling=scheduled)
