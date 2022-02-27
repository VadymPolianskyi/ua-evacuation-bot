from datetime import datetime

from cachetools import cached, TTLCache

from src.db.dao import AnnouncementDao
from src.db.entity import Announcement, AnnouncementType, AnnouncementServiceType
from src.service import time_service, cities


class AnnouncementService:
    def __init__(self):
        self.dao = AnnouncementDao()

    def create_home(self, user_id: int, a_type: AnnouncementType,
                    a_service: AnnouncementServiceType, city: str, info: str = None) -> Announcement:
        print(f"Create Announcement(user_id={user_id}, a_type={a_type.name}, " +
              f"a_service={a_service.name} city={city}, info={info})")
        a = Announcement(user_id=user_id, a_type=a_type, a_service=a_service, city_a=city, info=info)
        self.dao.save(a)
        print(f"Successfully created new "
              f"Announcement(user_id={user_id}, a_type={a_type.name}, " +
              f"a_service={a_service.name}, city={city}, info={info})")
        return a

    def create_trip(self, user_id: int, a_type: AnnouncementType,
                    a_service: AnnouncementServiceType, city_a: str,
                    city_b: str, info: str = None, scheduled: datetime = None) -> Announcement:
        print(f"Create Announcement(user_id={user_id}, a_type={a_type.name}, " +
              f"a_service={a_service.name}, city_a={city_a}, city_b={city_b}, " +
              f"info={info}, scheduled={scheduled})")
        a = Announcement(user_id=user_id, a_type=a_type, a_service=a_service,
                         city_a=city_a, city_b=city_b, info=info, scheduled=scheduled)
        self.dao.save(a)
        print(f"Successfully created new "
              f"Announcement(user_id={user_id}, a_type={a_type.name}, " +
              f"a_service={a_service.name}, city_a={city_a}, city_b={city_b}, " +
              f"info={info}, scheduled={scheduled})")
        return a

    def delete(self, announcement_id: str):
        print(f"Delete Announcement(announcement_id={announcement_id})")
        return self.dao.delete(announcement_id)

    @cached(cache=TTLCache(5, 5))
    def find(self, announcement_id: str):
        print(f"Find Announcement(announcement_id={announcement_id})")
        return self.dao.find(announcement_id)

    def find_by_user(self, user_id: int, a_type: AnnouncementType):
        print(f"Find Announcements(user_id={user_id}, a_type={a_type.name})")
        result = [a for a in self.dao.find_by_user(user_id) if a.a_type == a_type]
        print(f"Found {len(result)} Announcements(user_id={user_id}, a_type={a_type.name})")
        return result

    def find_by_city(self, city: str, a_type: AnnouncementType, a_service: AnnouncementServiceType, city_to=None):
        print(f"Find Announcements(a_type={a_type.name}, a_service={a_service.name}, city={city})")
        result = [a for a in self.dao.find_by_city(city) if
                  self.__is_needed_trip_announcement(a, a_type, a_service, city_to)]
        print(f"Found {len(result)} Announcements(a_type={a_type}, city={city})")
        return result

    def __is_needed_trip_announcement(self, a: Announcement, a_type, a_service, city_to) -> bool:
        result = a.a_type == a_type
        result = result and a.a_service == a_service
        result = result and (city_to is None or a.city_b in cities.any() or a.city_b == city_to)
        if a_service == AnnouncementServiceType.trip and a_type == AnnouncementType.share:
            result = time_service.validate(a.scheduled)
        return result
