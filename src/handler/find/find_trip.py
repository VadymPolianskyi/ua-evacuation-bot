from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.config import marker, msg, limits
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.find.find import FindGeneral
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.state import FindTripState
from src.service import cities, file_service
from src.service.announcement import AnnouncementService


class FindTripGeneral:
    async def _show_cities(self, message: Message, tg_msg: str, with_any: bool = False):
        cities_buttons = [[KeyboardButton(tz)] for tz in cities.all(with_any=with_any)]
        await message.answer(
            tg_msg,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))


class FindTripCallbackHandler(TelegramCallbackHandler, FindTripGeneral):
    MARKER = marker.FIND_TRIP

    def __init__(self):
        TelegramCallbackHandler.__init__(self)
        FindTripGeneral.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        await self._show_cities(callback.original.message, msg.FIND_TRIP_CITY_FROM)
        await FindTripState.waiting_for_city_from.set()


class FindTripCityFromAnswerHandler(TelegramMessageHandler, FindTripGeneral):
    def __init__(self):
        TelegramMessageHandler.__init__(self)
        FindTripGeneral.__init__(self)

    async def handle_(self, message: MessageMeta, *args):
        city_from = message.text

        if cities.validate(city_from):
            await self._show_cities(message.original, msg.FIND_TRIP_CITY_TO, with_any=True)
            await FindTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)
        else:
            await self._show_cities(message.original, msg.FIND_TRIP_CITY_FROM)
            await FindTripState.waiting_for_city_from.set()


class FindTripCityToAnswerHandler(TelegramMessageHandler, FindTripGeneral, FindGeneral):
    def __init__(self, announcement_service: AnnouncementService):
        TelegramMessageHandler.__init__(self)
        FindTripGeneral.__init__(self)
        FindGeneral.__init__(self)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        city_from = (await Dispatcher.get_current().current_state().get_data())['city_from']
        city_to = message.text

        if cities.validate(city_to) or city_to in cities.any():
            print_city_to = city_to
            if city_to in cities.any():
                city_to = None

            res = self.announcement_service.find_by_city(
                city_from, AnnouncementType.share, AnnouncementServiceType.trip, city_to)

            announcements: str = "\n" + "\n\n".join([a.to_str() for a in res]) if res else msg.FIND_NOTHING

            final_message = msg.FIND_TRIP_RESULT.format(city_from, print_city_to, announcements) \
                .replace('_', '\_')

            if len(final_message) > limits.FIND_RESPONSE_LIMIT:
                f = file_service.create_text_file(final_message, AnnouncementServiceType.trip.value, message.user_id)
                await message.original.answer_document(f, reply_markup=ReplyKeyboardRemove())
                file_service.close(f)
            else:
                await message.original.answer(final_message, reply_markup=ReplyKeyboardRemove())

            await Dispatcher.get_current().current_state().finish()
            await self._show_find_menu(message.original)
        else:
            await self._show_cities(message.original, msg.FIND_TRIP_CITY_TO, with_any=True)
            await FindTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)
