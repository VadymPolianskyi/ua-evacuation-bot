from typing import Optional

import pymysql

from src.config import config
from src.db.entity import Announcement


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

    def save(self, ann: Announcement):
        query = f"""
        INSERT INTO `{self.__table}` (`id`, `user_id`, `a_type`, `a_service`, `city_a`, `city_b`, `info`, `scheduled`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        self._execute(query,
                      (ann.id, ann.user_id, ann.a_type.name, ann.a_service.name,
                       ann.city_a, ann.city_b, ann.info, ann.scheduled))

    def find(self, announcement_id: str) -> Optional[Announcement]:
        print(f"Find Announcement({announcement_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE id=%s;'
        r = self._select_one(query, announcement_id)
        return Announcement.from_dict(r) if r else None

    def delete(self, announcement_id: str):
        print(f"Delete Announcement({announcement_id})")
        query = f'DELETE FROM `{self.__table}` WHERE id=%s'
        self._execute(query, announcement_id)

    def find_by_user(self, user_id: int) -> list:
        print(f"Select all Announcements for User({user_id})")
        query = f'SELECT * FROM `{self.__table}` WHERE user_id=%s;'
        result = self._select_list(query, user_id)
        print(f"Selected {len(result)} Announcements for User({user_id})")
        return [Announcement.from_dict(r) for r in result]

    def find_by_city(self, city: str) -> list:
        print(f"Select all Announcements for city {city}")
        query = f'SELECT * FROM `{self.__table}` WHERE city_a=%s;'
        result = self._select_list(query, city)
        print(f"Selected {len(result)} Announcements in city {city}")
        return [Announcement.from_dict(r) for r in result]
