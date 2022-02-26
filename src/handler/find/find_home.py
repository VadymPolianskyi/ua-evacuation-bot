from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.config import marker, msg, limits
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.find.find import FindGeneral
from src.handler.general import TelegramCallbackHandler, CallbackMeta, TelegramMessageHandler, MessageMeta
from src.handler.state import FindHomeState
from src.service import cities, file_service
from src.service.announcement import AnnouncementService


class FindHomeGeneral:
    async def _show_cities(self, message: Message):
        cities_buttons = [[KeyboardButton(tz)] for tz in cities.all()]
        await message.answer(
            msg.FIND_HOME_CITY,
            reply_markup=ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=False, one_time_keyboard=True))
        await FindHomeState.waiting_for_city.set()


class FindHomeCallbackHandler(TelegramCallbackHandler, FindHomeGeneral):
    MARKER = marker.FIND_HOME

    def __init__(self):
        TelegramCallbackHandler.__init__(self)
        FindHomeGeneral.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        await self._show_cities(callback.original.message)


class FindHomeCityAnswerHandler(TelegramMessageHandler, FindHomeGeneral, FindGeneral):
    def __init__(self, announcement_service: AnnouncementService):
        TelegramMessageHandler.__init__(self)
        FindHomeGeneral.__init__(self)
        FindGeneral.__init__(self)
        self.announcement_service = announcement_service

    async def handle_(self, message: MessageMeta, *args):
        city = message.text

        if cities.validate(city):
            res = self.announcement_service.find_by_city(city, AnnouncementType.share, AnnouncementServiceType.home)

            announcements: str = "\n" + "\n\n".join([a.to_str() for a in res]) if res else msg.FIND_NOTHING

            final_message = msg.FIND_HOME_RESULT.format(city, announcements)

            if len(final_message) > limits.FIND_RESPONSE_LIMIT:
                f = file_service.create_text_file(final_message, AnnouncementServiceType.home.value, message.user_id)
                await message.original.answer_document(f, reply_markup=ReplyKeyboardRemove())
                file_service.close(f)
            else:
                await message.original.answer(final_message, reply_markup=ReplyKeyboardRemove())

            await Dispatcher.get_current().current_state().finish()
            await self._show_find_menu(message.original)
        else:
            await self._show_cities(message.original)
            await FindHomeState.waiting_for_city.set()
