from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove

from src.config import msg, marker
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.find.find import FindGeneral
from src.handler.general import TelegramCallbackHandler, CallbackMeta
from src.service.announcement import AnnouncementService


class FindCreateCallbackHandler(TelegramCallbackHandler, FindGeneral):
    MARKER = marker.FIND_CREATE

    def __init__(self, announcement_service: AnnouncementService):
        TelegramCallbackHandler.__init__(self)
        FindGeneral.__init__(self, announcement_service)

    async def handle_(self, callback: CallbackMeta):
        state_data: dict = await Dispatcher.get_current().current_state().get_data()
        print(f"User({callback.user_id}): create Find Notificaiton")
        a_service = state_data['a_service']
        print(f"User({callback.user_id}): service = {a_service.value}")

        if a_service == AnnouncementServiceType.home:
            city: str = state_data['city']
            print(f"User({callback.user_id}): city = {city}")

            already_created = self.announcement_service.find_by_city(city, AnnouncementType.find,
                                                                     AnnouncementServiceType.home)
            print(f"User({callback.user_id}): already_created = {already_created}")

            if not already_created:
                self.announcement_service.create_home(callback.user_id, AnnouncementType.find,
                                                      AnnouncementServiceType.home, city)
        else:
            city_from: str = state_data['city_from']
            city_to: str = state_data['city_to']
            print(f"User({callback.user_id}): city_from = {city_from}, city_to = {city_to}")

            already_created = self.announcement_service.find_by_city(city_from, AnnouncementType.find,
                                                                     AnnouncementServiceType.trip, city_to)
            print(f"User({callback.user_id}): already_created = {already_created}")

            if not already_created:
                self.announcement_service.create_trip(callback.user_id, AnnouncementType.find,
                                                      AnnouncementServiceType.trip, city_from, city_to)
        print(f"User({callback.user_id}): notification creating is finished")

        await callback.original.message.answer(msg.FIND_CREATE_DONE, reply_markup=ReplyKeyboardRemove())

        await Dispatcher.get_current().current_state().finish()
        await self._show_find_menu(callback.original.message, callback.user_id)
