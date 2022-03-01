import logging
from typing import Optional

from cachetools import cached, TTLCache

from src.db.dao import CityDao
from src.db.entity import City


class CityService:
    ANY_ID = 1

    def __init__(self):
        self.dao = CityDao()

    @cached(cache=TTLCache(5, 5))
    def find_all_titles(self, except_of_id: int = None, with_any: bool = False) -> list:
        except_of_id = self.ANY_ID if not except_of_id else except_of_id
        result = self.find_all(except_of_id, with_any)
        return [c.name for c in result]

    @cached(cache=TTLCache(5, 5))
    def find_all(self, except_of_id: int = None, with_any: bool = False) -> list:
        logging.info(f"Find all Cities except {except_of_id}")
        result = [c for c in self.dao.find_all() if c.id != except_of_id]
        if with_any and except_of_id == self.ANY_ID:
            result = [self.find_any()] + result
        return result

    @cached(cache=TTLCache(5, 5))
    def find(self, city_id: int):
        if city_id:
            logging.info(f"Find City({city_id})")
            return self.dao.find(city_id)
        else:
            logging.warning(f"City({city_id}) is not found...")
            return None

    @cached(cache=TTLCache(5, 5))
    def find_any(self) -> City:
        return self.dao.find(self.ANY_ID)

    @cached(cache=TTLCache(5, 5))
    def find_by_name(self, city_name: str) -> Optional[City]:
        logging.info(f"Find by name City({city_name})")
        return self.dao.find_by_name(city_name)
