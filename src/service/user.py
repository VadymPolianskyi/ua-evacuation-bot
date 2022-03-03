from typing import Optional

from cachetools import cached, TTLCache

from src.db.dao import UserDao
from src.db.entity import User
import logging

from src.service import time_service


class UserService:
    def __init__(self):
        self.dao = UserDao()

    @cached(cache=TTLCache(60, 60))
    def find_or_create(self, user_id: int) -> Optional[User]:
        logging.debug(f"Get or Create User({user_id})")
        u = self.dao.find(user_id)
        if not self.dao.find(user_id):
            u = self.save(user_id)
        return u

    def save(self, user_id: str):
        logging.info(f"Create User({user_id})")
        u = User(user_id)
        self.dao.save(u)
        return u

    @cached(cache=TTLCache(1, 1))
    def count_last24_users(self):
        dt = time_service.minus(dt=time_service.now(), hours=24)
        todays_users = self.dao.count(dt)
        logging.info(f"Today's users - {todays_users}")
        return todays_users
