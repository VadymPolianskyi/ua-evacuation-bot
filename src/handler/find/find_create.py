import logging

from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove

from src.config import msg, marker
from src.db.entity import AnnouncementType, AnnouncementServiceType, City
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
        logging.info(f"User({callback.user_id}): create Find Notificaiton")
        a_service = state_data['a_service']
        logging.debug(f"User({callback.user_id}): service = {a_service.value}")

        if a_service == AnnouncementServiceType.home:
            city: City = state_data['city']
            logging.debug(f"User({callback.user_id}): city = {city.name}")

            already_created = self.announcement_service.find_by_city(city.id, AnnouncementType.find,
                                                                     AnnouncementServiceType.home)
            created_by_user = [a for a in already_created if a.user_id == callback.user_id]
            logging.info(f"User({callback.user_id}): created_by_user = {created_by_user}")

            if not created_by_user:
                self.announcement_service.create(callback.user_id, AnnouncementType.find,
                                                 AnnouncementServiceType.home, city.id)
        elif a_service == AnnouncementServiceType.trip:
            city_from: City = state_data['city_from']
            city_to: City = state_data['city_to']
            logging.debug(f"User({callback.user_id}): city_from = {city_from.name}, city_to = {city_to.name}")

            already_created = self.announcement_service.find_by_city(
                city_from_id=city_from.id,
                a_type=AnnouncementType.find,
                a_service=AnnouncementServiceType.trip,
                city_to_id=city_to.id)
            created_by_user = [a for a in already_created if a.user_id == callback.user_id]
            logging.info(f"User({callback.user_id}): created_by_user = {created_by_user}")

            if not created_by_user:
                self.announcement_service.create(callback.user_id, AnnouncementType.find,
                                                 AnnouncementServiceType.trip, city_from.id, city_to.id)

        else:
            city: City = state_data['city']
            logging.debug(f"User({callback.user_id}): city = {city.name}")

            already_created = self.announcement_service.find_by_city(city.id, AnnouncementType.find,
                                                                     AnnouncementServiceType.help)
            created_by_user = [a for a in already_created if a.user_id == callback.user_id]
            logging.info(f"User({callback.user_id}): created_by_user = {created_by_user}")

            if not created_by_user:
                self.announcement_service.create(callback.user_id, AnnouncementType.find,
                                                 AnnouncementServiceType.help, city.id)

        logging.info(f"User({callback.user_id}): notification creating is finished")

        await callback.original.message.answer(msg.FIND_CREATE_DONE, reply_markup=ReplyKeyboardRemove())

        await Dispatcher.get_current().current_state().finish()
        await self._show_find_menu(callback.original.message, callback.user_id)
