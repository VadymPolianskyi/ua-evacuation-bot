import uuid
from datetime import datetime

from src.config import msg
from src.db.entity import AnnouncementType, AnnouncementServiceType, City, AnnouncementEntity


class Announcement:
    def __init__(self,
                 user_id: int,
                 a_type: AnnouncementType,
                 a_service: AnnouncementServiceType,
                 city_from: City,

                 id: str = None,
                 info: str = None,
                 scheduled: datetime = None,
                 created: datetime = None,
                 city_to: City = None
                 ):
        self.id = uuid.uuid4() if id is None else id
        self.user_id: int = user_id
        self.a_type: AnnouncementType = a_type
        self.a_service: AnnouncementServiceType = a_service
        self.city_from: City = city_from
        self.city_to: City = city_to
        self.info: str = info
        self.scheduled: datetime = scheduled
        self.created: datetime = created

    def city(self) -> str:
        if self.a_service is AnnouncementServiceType.trip:
            return self.city_from.name + " - " + self.city_to.name
        else:
            return self.city_from.name

    def to_str(self):
        if self.a_type == AnnouncementType.share:
            if self.a_service == AnnouncementServiceType.home:
                result = msg.HOME_ANNOUNCEMENT.format(self.city_from.name)
            elif self.a_service == AnnouncementServiceType.help:
                result = msg.HELP_ANNOUNCEMENT.format(self.city_from.name)
            else:
                time = self.scheduled.strftime("%Y-%m-%d, %H:%M") if self.scheduled else msg.REGULAR
                result = msg.SHARE_TRIP_ANNOUNCEMENT.format(self.city_from.name, self.city_to.name, time)

            if self.created:
                created_date_str = self.created.strftime("%Y-%m-%d")
                result += msg.SHARE_CREATED_INFO.format(created_date_str, self.info)

            result += msg.SHARE_ANNOUNCEMENT_INFO.format(self.info)

        else:
            if self.a_service == AnnouncementServiceType.home:
                result = msg.HOME_ANNOUNCEMENT.format(self.city_from.name)
            elif self.a_service == AnnouncementServiceType.help:
                result = msg.HELP_ANNOUNCEMENT.format(self.city_from.name)
            else:
                result = msg.FIND_TRIP_ANNOUNCEMENT.format(self.city_from.name, self.city_to.name)

        return result

    @classmethod
    def from_entity(cls, ae: AnnouncementEntity, city_from: City, city_to: City = None):
        return Announcement(id=ae.id,
                            user_id=ae.user_id,
                            a_type=ae.a_type,
                            a_service=ae.a_service,
                            city_from=city_from,
                            city_to=city_to,
                            info=ae.info,
                            scheduled=ae.scheduled,
                            created=ae.created
                            )
