import logging

from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.config import marker, msg, limits
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.state import FindHomeState
from src.service import file_service, markup
from src.service.announcement import AnnouncementService
from src.service.city import CityService


class FindHomeGeneral:

    def __init__(self, city_service: CityService):
        self.city_service = city_service

    async def _show_cities(self, message: Message):
        cities_buttons = [[KeyboardButton(tz)] for tz in self.city_service.find_all_titles()]
        await message.answer(
            msg.FIND_HOME_CITY,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))
        await FindHomeState.waiting_for_city.set()

    async def _show_result(self, message: Message, final_message: str, user_id: int):
        logging.info(f"FindHome Final message: {final_message}")

        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_CREATE_BUTTON, marker.FIND_CREATE, '_'),
            (msg.BACK_BUTTON, marker.FIND, '_')
        ])

        if len(final_message) > limits.FIND_RESPONSE_LIMIT:
            logging.info(f"Response file becaulse of text length = {len(final_message)}")
            f = file_service.create_text_file(final_message, AnnouncementServiceType.home.value, user_id)
            await message.answer_document(f, reply_markup=menu_keyboard)
            file_service.close(f)
        else:
            await message.answer(final_message, reply_markup=menu_keyboard, disable_web_page_preview=True)


class FindHomeCallbackHandler(TelegramCallbackHandler, FindHomeGeneral):
    MARKER = marker.FIND_HOME

    def __init__(self, city_service: CityService):
        TelegramCallbackHandler.__init__(self)
        FindHomeGeneral.__init__(self, city_service)

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"FindHomeCallbackHandler.handle for User({callback.user_id})")
        await self._show_cities(callback.original.message)


class FindHomeCityAnswerHandler(TelegramMessageHandler, FindHomeGeneral):
    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        FindHomeGeneral.__init__(self, city_service)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        logging.info(f"FindHomeCityAnswerHandler.handle for User({message.user_id})")

        city_name = message.text
        logging.debug(f"Input city: {city_name}")

        city = self.city_service.find_by_name(city_name)

        if city and city.id != self.city_service.ANY_ID:
            logging.debug(f"Find "
                          f"Announcement(city={city.name}, type={AnnouncementType.share}, service={AnnouncementServiceType.home})")
            res = self.announcement_service.find_by_city(city.id, AnnouncementType.share, AnnouncementServiceType.home)

            logging.info(f"Found {len(res)}"
                         f"Announcement(city={city.name}, type={AnnouncementType.share}, service={AnnouncementServiceType.home})")
            announcements: str = "\n" + "\n\n".join([a.to_str() for a in res]) if res else msg.FIND_NOTHING

            final_message = msg.FIND_HOME_RESULT.format(city.name, announcements).replace('_', '\_')
            await self._show_result(message.original, final_message, message.user_id)

            await Dispatcher.get_current().current_state() \
                .update_data(a_service=AnnouncementServiceType.home, city=city)
        else:
            logging.info(f"Writing city again for User({message.user_id})")
            await self._show_cities(message.original)
            await FindHomeState.waiting_for_city.set()
