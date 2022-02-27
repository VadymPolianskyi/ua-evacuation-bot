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
        print(f"Final message: {final_message}")

        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_CREATE_BUTTON, marker.FIND_CREATE, '_'),
            (msg.BACK_BUTTON, marker.FIND, '_')
        ])

        if len(final_message) > limits.FIND_RESPONSE_LIMIT:
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
        await self._show_cities(callback.original.message)


class FindHomeCityAnswerHandler(TelegramMessageHandler, FindHomeGeneral):
    def __init__(self, announcement_service: AnnouncementService, city_service: CityService):
        TelegramMessageHandler.__init__(self)
        FindHomeGeneral.__init__(self, city_service)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        city_name = message.text
        city = self.city_service.find_by_name(city_name)

        if city and city.id != self.city_service.ANY_ID:
            res = self.announcement_service.find_by_city(city.id, AnnouncementType.share, AnnouncementServiceType.home)

            announcements: str = "\n" + "\n\n".join([a.to_str() for a in res]) if res else msg.FIND_NOTHING

            final_message = msg.FIND_HOME_RESULT.format(city.name, announcements).replace('_', '\_')
            await self._show_result(message.original, final_message, message.user_id)

            await Dispatcher.get_current().current_state() \
                .update_data(a_service=AnnouncementServiceType.home, city=city)
        else:
            await self._show_cities(message.original)
            await FindHomeState.waiting_for_city.set()
