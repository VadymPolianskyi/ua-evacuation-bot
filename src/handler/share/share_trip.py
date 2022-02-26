from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.config import marker, msg
from src.config.limits import INFO_SYMBOLS_LIMIT
from src.config.msg import SHARE_INFO_WARNING
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.share.share import ShareGeneral
from src.handler.state import ShareTripState
from src.service import cities, time_service
from src.service.announcement import AnnouncementService


class ShareTripGeneral:
    async def _show_cities(self, message: Message, tg_msg: str,
                           except_city: str = None,
                           with_any: bool = False):
        cities_buttons = [[KeyboardButton(tz)] for tz in cities.all(except_city, with_any)]
        await message.answer(
            tg_msg,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))


class ShareTripCallbackHandler(TelegramCallbackHandler, ShareTripGeneral):
    MARKER = marker.SHARE_TRIP

    def __init__(self):
        TelegramCallbackHandler.__init__(self)
        ShareTripGeneral.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        await self._show_cities(callback.original.message, msg.SHARE_TRIP_CITY_FROM)
        await ShareTripState.waiting_for_city_from.set()


# city from
class ShareTripCityFromAnswerHandler(TelegramMessageHandler, ShareTripGeneral):
    def __init__(self, ):
        TelegramMessageHandler.__init__(self)
        ShareTripGeneral.__init__(self)

    async def handle_(self, message: MessageMeta, *args):
        city_from = message.text

        if cities.validate(city_from):
            await self._show_cities(message.original, msg.SHARE_TRIP_CITY_TO,
                                    except_city=city_from,
                                    with_any=True)
            await ShareTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)
        else:
            await self._show_cities(message.original, msg.SHARE_TRIP_CITY_FROM)
            await ShareTripState.waiting_for_city_from.set()


# city to
class ShareTripCityToAnswerHandler(TelegramMessageHandler, ShareTripGeneral):
    def __init__(self, ):
        TelegramMessageHandler.__init__(self)
        ShareTripGeneral.__init__(self)

    async def handle_(self, message: MessageMeta, *args):
        city_from = (await Dispatcher.get_current().current_state().get_data())['city_from']
        city_to = message.text

        if cities.validate(city_to) or city_to in cities.any():
            await message.original.answer(msg.SHARE_TRIP_SCHEDULING)
            await ShareTripState.waiting_for_scheduling.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to)
        else:
            await self._show_cities(message.original, msg.SHARE_TRIP_CITY_TO,
                                    except_city=city_from,
                                    with_any=True)
            await ShareTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)


# scheduling
class ShareTripSchedulingAnswerHandler(TelegramMessageHandler, ShareTripGeneral):
    def __init__(self, ):
        TelegramMessageHandler.__init__(self)
        ShareTripGeneral.__init__(self)

    async def handle_(self, message: MessageMeta, *args):
        state_data: dict = await Dispatcher.get_current().current_state().get_data()
        city_from = state_data['city_from']
        city_to = state_data['city_to']
        scheduling = message.text

        extracted_schedule: datetime = time_service.extract_datetime(scheduling)

        if extracted_schedule:
            await message.original.answer(msg.SHARE_TRIP_INFO)
            await ShareTripState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to,
                                                                       scheduling=extracted_schedule)
        else:
            await self._show_cities(message.original, msg.SHARE_TRIP_SCHEDULING)
            await ShareTripState.waiting_for_scheduling.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to)


class ShareTripInfoAnswerHandler(TelegramMessageHandler, ShareGeneral):
    def __init__(self, announcement_service: AnnouncementService):
        TelegramMessageHandler.__init__(self)
        ShareGeneral.__init__(self)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        state_data: dict = await Dispatcher.get_current().current_state().get_data()
        city_from: str = state_data['city_from']
        city_to: str = state_data['city_to']
        scheduling: datetime = state_data['scheduling']

        info = message.text

        if len(info) <= INFO_SYMBOLS_LIMIT:

            self.announcement_service.create_trip(message.user_id, AnnouncementType.share,
                                                  AnnouncementServiceType.trip, city_from, city_to, info, scheduling)
            # todo: find all for this city and send them
            await message.original.answer(msg.SHARE_TRIP_DONE.format(city_from, city_to, info, scheduling))
            await Dispatcher.get_current().current_state().finish()
            await self._show_share_menu(message.original)
        else:
            diff = len(info) - INFO_SYMBOLS_LIMIT

            await message.original.answer(SHARE_INFO_WARNING.format(diff) + "\n" + msg.SHARE_TRIP_INFO)
            await ShareTripState.waiting_for_info.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from, city_to=city_to,
                                                                       scheduling=scheduling)
