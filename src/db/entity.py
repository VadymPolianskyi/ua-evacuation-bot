import uuid
from datetime import datetime
from enum import Enum

from src.config import msg
from src.config.msg import TRIP_TYPE_NAME, HOME_TYPE_NAME, HELP_TYPE_NAME

VERIFIED_STATUS = 'VERIFIED'


class AnnouncementType(Enum):
    find = 1
    share = 2


class AnnouncementServiceType(Enum):
    home = HOME_TYPE_NAME
    trip = TRIP_TYPE_NAME
    help = HELP_TYPE_NAME


class User:
    def __init__(self, id: str, created: datetime = None):
        self.id = id
        self.created = created

    @classmethod
    def from_dict(cls, r):
        return User(id=r['id'], created=r['created'])


class City:
    def __init__(self, name: str, country: str, id: int = None):
        self.id = id
        self.name = name
        self.country = country

    @classmethod
    def from_dict(cls, r):
        return City(id=r['id'], name=r['name'], country=r['country'])


class AnnouncementEntity:
    def __init__(self,
                 user_id: int,
                 a_type: AnnouncementType,
                 a_service: AnnouncementServiceType,
                 city_from_id: int,

                 info: str = None,
                 verified: bool = False,
                 verified_at: datetime = None,
                 id: str = None,
                 scheduled: datetime = None,
                 created: datetime = None,
                 city_to_id: int = None
                 ):
        self.id = uuid.uuid4() if id is None else id
        self.user_id: int = user_id
        self.a_type: AnnouncementType = a_type
        self.a_service: AnnouncementServiceType = a_service
        self.city_from_id: int = city_from_id
        self.city_to_id: int = city_to_id
        self.info: str = info
        self.verified: bool = verified
        self.verified_at: datetime = verified_at
        self.scheduled: datetime = scheduled
        self.created: datetime = created

    def to_str(self):
        return f"AnnouncementEntity(user_id={self.user_id}, a_type={self.a_type.name}, " \
               f"a_service={self.a_service.name}, city_from_id={self.city_from_id}, city_to_id={self.city_to_id}, " \
               f"info={self.info}, verified={self.verified}, verified_at={self.verified_at}, scheduled={self.scheduled})"

    @classmethod
    def from_dict(cls, r):
        a_type = AnnouncementType.share if r['a_type'] == AnnouncementType.share.name else AnnouncementType.find
        if r['a_service'] == AnnouncementServiceType.home.name:
            a_service = AnnouncementServiceType.home
        elif r['a_service'] == AnnouncementServiceType.trip.name:
            a_service = AnnouncementServiceType.trip
        else:
            a_service = AnnouncementServiceType.help

        if 'status' in r.keys() and r['status'] == VERIFIED_STATUS:
            verified = True
            verified_at = r['updated_at']
        else:
            verified = False
            verified_at = None

        return AnnouncementEntity(id=r['id'],
                                  user_id=r['user_id'],
                                  a_type=a_type,
                                  a_service=a_service,
                                  city_from_id=r['city_from_id'],
                                  city_to_id=r['city_to_id'],
                                  info=r['info'],
                                  verified=verified,
                                  verified_at=verified_at,
                                  scheduled=r['scheduled'],
                                  created=r['created']
                                  )


class BlockedUser:
    def __init__(self,
                 id: int,
                 contact: str,
                 info: str):
        self.id = id
        self.contact = contact
        self.info = info

    @classmethod
    def from_dict(cls, r):
        return BlockedUser(id=r['id'], contact=r['contact'], info=r['info'])

    def to_str(self):
        return msg.BLOCKED_USER.format(self.contact, self.info)
