import asyncio
import logging
from datetime import datetime

from aiogram import Bot

from src.config import msg, config
from src.db.entity import AnnouncementType
from src.model import Announcement
from src.service import time_service
from src.service.announcement import AnnouncementService


class Notificator:
    def __init__(self, interval_min: int):
        self.bot = Bot(token=config.BOT_API_TOKEN, parse_mode=config.PARSE_MODE)
        self.announcement_service = AnnouncementService()
        self.interval_min = interval_min
        self.el = asyncio.new_event_loop()

    def notify_about_last(self):
        announcement_service = AnnouncementService()
        interval_min = config.NOTIFICATIONS_INTERVAL

        logging.info(f"Nofify about last announcements. Interval - {interval_min}")

        after_timestamp: datetime = time_service.minus(dt=time_service.now_utc(), minutes=interval_min)
        logging.debug(f"After timestamp - {after_timestamp}")

        last_announcements = announcement_service.find_all_after(AnnouncementType.share, after_timestamp)

        for a in last_announcements:
            self.notify(announcement_service, a)
        logging.info(f"Successfully notified about last {len(last_announcements)} announcements")
        self.announcement_service.close()
        self.bot.close()
        self.el.close()

    def notify(self, announcement_service: AnnouncementService, a: Announcement):
        city_to_id = a.city_to.id if a.city_to else None
        announcements_find = announcement_service.find_by_city(
            a.city_from.id, AnnouncementType.find, a.a_service, city_to_id)
        users = [ann.user_id for ann in announcements_find]

        a_str = a.to_str()
        bot = Bot(token=config.BOT_API_TOKEN, parse_mode=config.PARSE_MODE)

        for user_id in users:
            try:
                logging.info(f"Notify User({user_id}) about Announcement({a_str})")
                self.el.run_until_complete(bot.send_message(user_id, msg.FOUND.format(a_str)))
            except Exception as e:
                logging.error("Failed notification User({user_id}) about Announcement({a_str})", e)
