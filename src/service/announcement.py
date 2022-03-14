import logging
from datetime import datetime

from cachetools import cached, TTLCache

from src.db.dao import AnnouncementDao
from src.db.entity import AnnouncementEntity, AnnouncementType, AnnouncementServiceType
from src.model import Announcement
from src.service import time_service
from src.service.city import CityService


class AnnouncementService:
    def __init__(self):
        self.dao = AnnouncementDao()
        self.cities = CityService()

    def create(self, user_id: int, a_type: AnnouncementType,
               a_service: AnnouncementServiceType, city_from_id: int,
               city_to_id: int = None, info: str = None, scheduled: datetime = None) -> Announcement:
        logging.debug("Create announcement")
        info = info.replace(";", " ") if info else None

        ae = AnnouncementEntity(user_id=user_id, a_type=a_type, a_service=a_service,
                                city_from_id=city_from_id, city_to_id=city_to_id, info=info, scheduled=scheduled)
        self.dao.save(ae)
        logging.info(f"Successfully created new {ae.to_str()}")
        return Announcement.from_entity(ae, self.cities.find(city_from_id), self.cities.find(city_to_id))

    def delete(self, announcement_id: str):
        logging.info(f"Delete AnnouncementEntity(id={announcement_id})")
        return self.dao.delete(announcement_id)

    @cached(cache=TTLCache(maxsize=100, ttl=60))
    def find(self, announcement_id: str) -> Announcement:
        logging.debug(f"Find Announcement(id={announcement_id})")
        ae = self.dao.find(announcement_id)
        logging.info(f"Found {ae.to_str()}")
        return self.__to_model(ae)

    @cached(cache=TTLCache(maxsize=10, ttl=30))
    def count_all(self, a_type: AnnouncementType = AnnouncementType.share):
        todays_announcements = self.dao.count(a_type)
        logging.info(f"Today's announcements - {todays_announcements}")
        return todays_announcements

    def find_all(self):
        result = [self.__to_model(ae) for ae in self.dao.find_all()]
        logging.info(f"Found {len(result)} Announcements")
        return result

    def find_by_user(self, user_id: int, a_type: AnnouncementType) -> list:
        logging.debug(f"Find Announcements(user_id={user_id}, a_type={a_type.name})")
        result = [self.__to_model(ae) for ae in self.dao.find_by_user(user_id) if ae.a_type == a_type]
        logging.info(f"Found {len(result)} Announcements(user_id={user_id}, a_type={a_type.name})")
        return result

    def find_by_city(self, city_from_id: int, a_type: AnnouncementType, a_service: AnnouncementServiceType,
                     city_to_id=None):
        logging.debug(f"Find Announcements(a_type={a_type},city_from_id={city_from_id},city_to_id={city_to_id})")

        all_selected = self.dao.find_by_city(city_from_id)

        result = [self.__to_model(ae) for ae in all_selected if
                  self.__is_needed_announcement(ae, a_type, a_service, city_to_id)]
        logging.info(f"Found {len(result)}: a_type={a_type}, city_from_id={city_from_id}, city_to_id={city_to_id})")
        return result

    def __is_needed_announcement(self, a: AnnouncementEntity, a_type, a_service, city_to_id: int) -> bool:
        result = a.a_type == a_type
        result = result and a.a_service == a_service
        result = result and (city_to_id is None or a.city_to_id == city_to_id
                             or a.city_to_id == self.cities.ANY_ID or city_to_id == self.cities.ANY_ID)
        if result and a.scheduled is not None:
            result = result and time_service.validate(a.scheduled)
        logging.debug(f"Is needed = {result}: {a.to_str()}| "
                      f"Announcement(a_type={a_type}, a_service={a_service}, city_to_id={city_to_id})")
        return result

    def __to_model(self, ae: AnnouncementEntity) -> Announcement:
        return Announcement.from_entity(ae, self.cities.find(ae.city_from_id), self.cities.find(ae.city_to_id))

    def find_all_after(self, a_type: AnnouncementType, from_timestamp: datetime):
        logging.debug(f"Find Announcements(a_type={a_type.name}, from_timestamp={from_timestamp})")
        result = [self.__to_model(ae) for ae in self.dao.find_after(a_type, from_timestamp)]
        logging.info(f"Found {len(result)}: a_type={a_type.name}, from_timestamp={from_timestamp})")
        return result

    def close(self):
        self.dao.close()
        self.cities.close()
