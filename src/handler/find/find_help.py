import logging

from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.config import marker, msg
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.find.find import FindGeneral
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.state import FindHelpState
from src.service.announcement import AnnouncementService
from src.service.city import CityService

A_SERVICE = AnnouncementServiceType.help


class FindHelpGeneral:

    def __init__(self, city_service: CityService):
        self.city_service = city_service

    async def _show_cities(self, message: Message):
        cities_buttons = [[KeyboardButton(tz)] for tz in self.city_service.find_all_titles()]
        await message.answer(
            msg.FIND_HELP_CITY,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))
        await FindHelpState.waiting_for_city.set()


class FindHelpCallbackHandler(TelegramCallbackHandler, FindHelpGeneral):
    MARKER = marker.FIND_HELP

    def __init__(self, city_service: CityService):
        TelegramCallbackHandler.__init__(self)
        FindHelpGeneral.__init__(self, city_service)

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"FindHelpCallbackHandler.handle for User({callback.user_id})")
        await self._show_cities(callback.original.message)


class FindHelpCityAnswerHandler(TelegramMessageHandler, FindHelpGeneral, FindGeneral):
    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        FindHelpGeneral.__init__(self, city_service)
        FindGeneral.__init__(self, announcement_service)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"FindHelpCityAnswerHandler.handle for User({message.user_id})")

        city_name = message.text
        logging.debug(f"Input city: {city_name}")

        city = self.city_service.find_by_name(city_name)

        if city and city.id != self.city_service.ANY_ID:
            logging.debug(f"Find "
                          f"Announcement(city={city.name}, type={AnnouncementType.share}, service={A_SERVICE})")
            res = self.announcement_service.find_by_city(city.id, AnnouncementType.share, A_SERVICE)

            logging.info(f"Found {len(res)}"
                         f"Announcement(city={city.name}, type={AnnouncementType.share}, service={A_SERVICE})")
            announcements: str = "\n" + "\n\n".join([a.to_str() for a in res]) if res else msg.FIND_NOTHING

            final_message = msg.FIND_HELP_RESULT.format(city.name, announcements).replace('_', '\_')
            await self._show_result(message.original, final_message)

            await Dispatcher.get_current().current_state() \
                .update_data(a_service=A_SERVICE, city=city)
        else:
            logging.info(f"Writing city again for User({message.user_id})")
            await self._show_cities(message.original)
            await FindHelpState.waiting_for_city.set()
