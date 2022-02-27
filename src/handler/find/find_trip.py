from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.config import marker, msg, limits
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.state import FindTripState
from src.service import cities, file_service, markup
from src.service.announcement import AnnouncementService


class FindTripGeneral:
    async def _show_cities(self, message: Message, tg_msg: str, with_any: bool = False):
        cities_buttons = [[KeyboardButton(tz)] for tz in cities.all(with_any=with_any)]
        await message.answer(
            tg_msg,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))

    async def _show_result(self, message: Message, final_message: str, user_id: int):
        print(f"Final message: {final_message}")

        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_CREATE_BUTTON, marker.FIND_CREATE, '_'),
            (msg.BACK_BUTTON, marker.FIND, '_')
        ])

        if len(final_message) > limits.FIND_RESPONSE_LIMIT:
            f = file_service.create_text_file(final_message, AnnouncementServiceType.trip.value, user_id)
            await message.answer_document(f, reply_markup=menu_keyboard)
            file_service.close(f)
        else:
            await message.answer(final_message, reply_markup=menu_keyboard)


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


class FindTripCityToAnswerHandler(TelegramMessageHandler, FindTripGeneral):
    def __init__(self, announcement_service: AnnouncementService):
        TelegramMessageHandler.__init__(self)
        FindTripGeneral.__init__(self)
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

            final_message = msg.FIND_TRIP_RESULT.format(city_from, print_city_to, announcements).replace('_', '\_')
            await self._show_result(message.original, final_message, message.user_id)

            await Dispatcher.get_current().current_state().update_data(
                a_service=AnnouncementServiceType.trip, city_from=city_from, city_to=city_to)
        else:
            await self._show_cities(message.original, msg.FIND_TRIP_CITY_TO, with_any=True)
            await FindTripState.waiting_for_city_to.set()
            await Dispatcher.get_current().current_state().update_data(city_from=city_from)
