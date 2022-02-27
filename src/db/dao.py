from typing import Optional

import pymysql

from src.config import config
from src.db.entity import AnnouncementEntity, City


def create_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USERNAME,
        passwd=config.DB_PASSWORD,
        database=config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)


connection = create_connection()


class Dao:
    def _select_one(self, query, parameters):
        global connection
        try:
            with connection.cursor() as cursor:
                sql_query = query.replace("'", "")
                print(f"Execute 'select_one' query: {sql_query}")
                print(f'Parameters: {parameters}')
                cursor.execute(sql_query, parameters)
                print("Successfully selected")
                return cursor.fetchone()
        except Exception as e:
            print("Exception in db:", e)
            connection = create_connection()
            print("Recreated connection")

    def _select_list(self, query, parameters) -> list:
        global connection
        try:
            with connection.cursor() as cursor:
                sql_query = query.replace("'", "")
                print(f"Execute 'select_list' query: {sql_query}")
                print(f'Parameters: {parameters}')
                cursor.execute(sql_query, parameters)
                print("Successfully selected")
                return cursor.fetchall()
        except Exception as e:
            print("Exception in db:", e)
            connection = create_connection()
            print("Recreated connection")

    def _execute(self, query, parameters):
        global connection
        try:
            with connection.cursor() as cursor:
                sql_query = query.replace("'", "")
                print(f"Execute query: {sql_query}")
                print(f'Parameters: {parameters}')
                cursor.execute(sql_query, parameters)
                print("Successfully executed")
            connection.commit()
        except Exception as e:
            print("Exception in db:", e)
            connection = create_connection()
            print("Recreated connection")


class AnnouncementDao(Dao):
    def __init__(self):
        self.__table = config.DB_TABLE_ANNOUNCEMENT

    def save(self, ann: AnnouncementEntity):
        query = f"""
        INSERT INTO `{self.__table}` 
        (`id`, `user_id`, `a_type`, `a_service`, `city_from_id`, `city_to_id`, `info`, `scheduled`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        self._execute(query,
                      (ann.id, ann.user_id, ann.a_type.name, ann.a_service.name,
                       ann.city_from_id, ann.city_to_id, ann.info, ann.scheduled))

    def find(self, announcement_id: str) -> Optional[AnnouncementEntity]:
        print(f"Find Announcement({announcement_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE id=%s;'
        r = self._select_one(query, announcement_id)
        return AnnouncementEntity.from_dict(r) if r else None

    def delete(self, announcement_id: str):
        print(f"Delete Announcement({announcement_id})")
        query = f'DELETE FROM `{self.__table}` WHERE id=%s'
        self._execute(query, announcement_id)

    def find_by_user(self, user_id: int) -> list:
        print(f"Select all Announcements for User({user_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE user_id=%s;'
        result = self._select_list(query, user_id)
        print(f"Selected {len(result)} Announcements for User({user_id})")
        return [AnnouncementEntity.from_dict(r) for r in result]

    def find_by_city(self, city_from_id: int) -> list:
        print(f"Select all Announcements for city {city_from_id}")
        query = f'SELECT * FROM `{self.__table}` WHERE city_from_id=%s;'
        result = self._select_list(query, city_from_id)
        print(f"Selected {len(result)} Announcements in city {city_from_id}")
        return [AnnouncementEntity.from_dict(r) for r in result]

    def find_all(self):
        print(f"Select all Announcements")
        query = f'SELECT * FROM `{self.__table}`;'
        result = self._select_list(query, ())
        print(f"Selected {len(result)} Announcements")
        return [AnnouncementEntity.from_dict(r) for r in result]

    def update(self, a: AnnouncementEntity):
        query = f'UPDATE `{self.__table}` SET city_from_id = %s, city_to_id = %s WHERE id=%s;'
        self._execute(query, (a.city_from_id, a.city_to_id, a.id))


class CityDao(Dao):
    def __init__(self):
        self.__table = config.DB_TABLE_CITY

    def save(self, city: City):
        query = f"""
        INSERT INTO `{self.__table}` (`name`, `country`) 
        VALUES (%s, %s);
        """
        self._execute(query, (city.name, city.country))

    def find(self, city_id: int) -> Optional[City]:
        print(f"Find City({city_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE id=%s;'
        r = self._select_one(query, city_id)
        return City.from_dict(r) if r else None

    def find_all(self) -> list:
        print(f"Select all Cities")
        query = f'SELECT * FROM `{self.__table}`;'
        result = self._select_list(query, ())
        print(f"Selected {len(result)} Cities")
        return [City.from_dict(r) for r in result]

    def find_by_name(self, city_name: str):
        print(f"Find City({city_name})")
        query = f'SELECT * FROM `{self.__table}` WHERE name=%s;'
        r = self._select_one(query, city_name)
        return City.from_dict(r) if r else None
