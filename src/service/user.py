from typing import Optional

from cachetools import cached, TTLCache

from src.db.dao import UserDao
from src.db.entity import User


class UserService:
    def __init__(self):
        self.dao = UserDao()

    @cached(cache=TTLCache(60, 60))
    def find_or_create(self, user_id: int) -> Optional[User]:
        u = self.dao.find(user_id)
        if not self.dao.find(user_id):
            u = self.save(user_id)
        return u

    def save(self, user_id: str):
        u = User(user_id)
        self.dao.save(u)
        return u
