import datetime
import logging
from typing import Optional

import pymysql
from pymysql import err

from src.config import config
from src.db.entity import AnnouncementEntity, City, User, AnnouncementType, BlockedUser


def create_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USERNAME,
        passwd=config.DB_PASSWORD,
        database=config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)


ADMIN_ID_MAX = 1000


class Dao:

    def __init__(self):
        self.connection = create_connection()

    def _select_one(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                sql_query = query.replace("'", "")
                logging.debug(f"Execute 'select_one' query: {sql_query}")
                logging.debug(f'Parameters: {parameters}')
                cursor.execute(sql_query, parameters)
                logging.debug("Successfully selected")
                return cursor.fetchone()
        except Exception as e:
            logging.error("Exception in db:", e)
            self.connection = create_connection()
            logging.info("Recreated connection")
            return self._select_one(query, parameters)

    def _select_list(self, query, parameters) -> list:
        try:
            with self.connection.cursor() as cursor:
                sql_query = query.replace("'", "")
                logging.debug(f"Execute 'select_list' query: {sql_query}")
                logging.debug(f'Parameters: {parameters}')
                cursor.execute(sql_query, parameters)
                logging.debug("Successfully selected")
                return cursor.fetchall()
        except Exception as e:
            logging.error("Exception in db:", e)
            self.connection = create_connection()
            logging.info("Recreated connection")
            return self._select_list(query, parameters)

    def _execute(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                sql_query = query.replace("'", "")
                logging.debug(f"Execute query: {sql_query}")
                logging.debug(f'Parameters: {parameters}')
                cursor.execute(sql_query, parameters)
                logging.debug("Successfully executed")
            self.connection.commit()
        except Exception as e:
            logging.error("Exception in db:", e)
            self.connection = create_connection()
            logging.info("Recreated connection")
            return self._execute(query, parameters)

    def close(self):
        logging.info("Closing connection")
        try:
            self.connection.close()
        except err.Error as e:
            logging.info(f"Exception during closing connection", e)


class AnnouncementDao(Dao):
    def __init__(self):
        super().__init__()
        self.__table = config.DB_TABLE_ANNOUNCEMENT

    def save(self, ann: AnnouncementEntity, approved=True):
        logging.debug(f"Create {ann.to_str()}")
        query = f"""
        INSERT INTO `{self.__table}` 
        (`id`, `user_id`, `a_type`, `a_service`, `city_from_id`, `city_to_id`, `info`, `scheduled`, `approved`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        self._execute(query,
                      (ann.id, ann.user_id, ann.a_type.name, ann.a_service.name,
                       ann.city_from_id, ann.city_to_id, ann.info, ann.scheduled, approved))

    def find(self, announcement_id: str) -> Optional[AnnouncementEntity]:
        logging.debug(f"Find Announcement({announcement_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE id=%s;'
        r = self._select_one(query, announcement_id)
        return AnnouncementEntity.from_dict(r) if r else None

    def delete(self, announcement_id: str):
        logging.debug(f"Delete Announcement({announcement_id})")
        query = f'UPDATE `{self.__table}` SET approved = %s WHERE id=%s;'
        self._execute(query, (False, announcement_id))

    def find_by_user(self, user_id: int, approved=True) -> list:
        logging.debug(f"Select all Announcements for User({user_id})")
        query = f"""
        SELECT a.*, c.status, c.updated_at FROM `{self.__table}` AS a
        LEFT JOIN evacuation_call_status as c ON a.id = c.announcement_id
        WHERE user_id=%s and approved=%s ORDER BY created;
        """
        result = self._select_list(query, (user_id, approved))
        logging.debug(f"Selected {len(result)} Announcements for User({user_id})")
        return [AnnouncementEntity.from_dict(r) for r in result]

    def find_by_city(self, city_from_id: int, approved=True) -> list:
        logging.debug(f"Select all Announcements for city {city_from_id}")
        query = f"""
        SELECT a.*, c.status, c.updated_at FROM `{self.__table}` AS a
        LEFT JOIN evacuation_call_status as c ON a.id = c.announcement_id
        WHERE city_from_id=%s and approved=%s ORDER BY created;
        """
        result = self._select_list(query, (city_from_id, approved))
        logging.debug(f"Selected {len(result)} Announcements in city {city_from_id}")
        return [AnnouncementEntity.from_dict(r) for r in result]

    def find_all(self):
        logging.debug(f"Select all Announcements")
        query = f'SELECT * FROM `{self.__table}`;'
        result = self._select_list(query, ())
        logging.debug(f"Selected {len(result)} Announcements")
        return [AnnouncementEntity.from_dict(r) for r in result]

    def count(self, a_type: AnnouncementType, from_date: datetime.date = None):
        logging.debug(f"Find Announcements({a_type.name}) count from date - {from_date})")
        from_date_condition = "AND created > %s" if from_date else ""
        from_date_parameters: tuple = (a_type, from_date) if from_date else (a_type.name)

        query = f'SELECT count(*) as res FROM `{self.__table}` WHERE a_type=%s {from_date_condition} AND approved=True;'
        r = self._select_one(query, from_date_parameters)
        return r['res'] if r else None

    def find_after(self, a_type: AnnouncementType, after_timestamp: datetime, approved=True):
        logging.debug(f"Select all Announcements({a_type.name}) after_timestamp {after_timestamp}")
        query = f'SELECT * FROM `{self.__table}` WHERE a_type=%s AND created >= %s AND user_id<=%s AND approved=%s ORDER BY created;'
        result = self._select_list(query, (a_type.name, after_timestamp, ADMIN_ID_MAX, approved))
        logging.debug(f"Selected {len(result)} Announcements({a_type.name}) after_timestamp {after_timestamp}")
        return [AnnouncementEntity.from_dict(r) for r in result]


class CityDao(Dao):
    def __init__(self):
        super().__init__()
        self.__table = config.DB_TABLE_CITY

    def save(self, city: City):
        logging.debug(f"Save City({city.name})")
        query = f"""
        INSERT INTO `{self.__table}` (`name`, `country`) 
        VALUES (%s, %s);
        """
        self._execute(query, (city.name, city.country))

    def find(self, city_id: int) -> Optional[City]:
        logging.debug(f"Find City({city_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE id=%s;'
        r = self._select_one(query, city_id)
        return City.from_dict(r) if r else None

    def find_all(self) -> list:
        logging.debug(f"Select all Cities")
        query = f'SELECT * FROM `{self.__table}`;'
        result = self._select_list(query, ())
        logging.debug(f"Selected {len(result)} Cities")
        return [City.from_dict(r) for r in result]

    def find_by_name(self, city_name: str):
        logging.debug(f"Find City({city_name})")
        query = f'SELECT * FROM `{self.__table}` WHERE name=%s;'
        r = self._select_one(query, city_name)
        return City.from_dict(r) if r else None


class UserDao(Dao):
    def __init__(self):
        super().__init__()
        self.__table = config.DB_TABLE_USER

    def save(self, user: User):
        query = f"""
        INSERT INTO `{self.__table}` (`id`) 
        VALUES (%s);
        """
        self._execute(query, (user.id))

    def find(self, user_id: int) -> Optional[City]:
        logging.debug(f"Find User({user_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE id=%s;'
        r = self._select_one(query, (user_id))
        return User.from_dict(r) if r else None

    def count(self, from_date: datetime.date = None):
        logging.debug(f"Find Users count from date - {from_date})")
        from_date_condition = "WHERE created > %s" if from_date else ""
        from_date_parameters: tuple = (from_date) if from_date else ()

        query = f'SELECT count(*) as res FROM `{self.__table}` {from_date_condition} ;'
        r = self._select_one(query, from_date_parameters)
        return r['res'] if r else None


class BlockedUserDao(Dao):
    def __init__(self):
        super().__init__()
        self.__table = config.DB_TABLE_BLOCKED_USER

    def find_all(self) -> list:
        logging.debug(f"Select all BlockedUsers")
        query = f'SELECT * FROM `{self.__table}`;'
        result = self._select_list(query, ())
        logging.debug(f"Selected {len(result)} BlockedUsers")
        return [BlockedUser.from_dict(r) for r in result]
