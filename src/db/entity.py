import uuid
from datetime import datetime
from enum import Enum

from src.config.msg import TRIP_TYPE_NAME, HOME_TYPE_NAME


class AnnouncementType(Enum):
    find = 1
    share = 2


class AnnouncementServiceType(Enum):
    home = HOME_TYPE_NAME
    trip = TRIP_TYPE_NAME


class Announcement:
    def __init__(self,
                 user_id: int,
                 a_type: AnnouncementType,
                 a_service: AnnouncementServiceType,
                 city_a: str,
                 info: str = None,
                 id: str = None,
                 city_b: str = None,
                 scheduled: datetime = None,
                 created: datetime = None
                 ):
        self.id = uuid.uuid4() if id is None else id
        self.user_id: int = user_id
        self.a_type: AnnouncementType = a_type
        self.a_service: AnnouncementServiceType = a_service
        self.city_a: str = city_a
        self.city_b: str = city_b
        self.info: str = info
        self.scheduled: datetime = scheduled
        self.created: datetime = created

    def city(self) -> str:
        if self.a_service is AnnouncementServiceType.home:
            return self.city_a
        else:
            return self.city_a + " - " + self.city_b

    def to_str(self):
        if self.a_type == AnnouncementType.share:
            if self.a_service == AnnouncementServiceType.home:
                return f"Житло 🏠 `{self.city_a}`\nІнформація: {self.info}"
            else:
                time = self.scheduled.strftime("%Y-%m-%d, %H:%M")
                return f"Транспорт 🚗 `{self.city_a}` - `{self.city_b}`\nЧас: {time}\nІнформація: {self.info}"
        else:
            if self.a_service == AnnouncementServiceType.home:
                return f"Житло 🏠 `{self.city_a}`"
            else:
                return f"Транспорт 🚗 `{self.city_a}` - `{self.city_b}`"

    @classmethod
    def from_dict(cls, r):
        a_type = AnnouncementType.share if r['a_type'] == "share" else AnnouncementType.find
        a_service = AnnouncementServiceType.home if r['a_service'] == "home" else AnnouncementServiceType.trip
        return Announcement(id=r['id'],
                            user_id=r['user_id'],
                            a_type=a_type,
                            a_service=a_service,
                            city_a=r['city_a'],
                            city_b=r['city_b'],
                            info=r['info'],
                            scheduled=r['scheduled'],
                            created=r['created']
                            )
