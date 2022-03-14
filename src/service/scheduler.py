import logging
import threading

from src.config import config
from src.service import time_service
from src.service.notificator import Notificator


class Scheduler:
    def run(self):
        t = threading.Timer(time_service.to_minutes(config.NOTIFICATIONS_INTERVAL), self.run_)
        t.start()
        logging.info(f"Successfully scheduled Notificator. Every {config.NOTIFICATIONS_INTERVAL} minutes")

    def run_(self):
        Notificator(config.NOTIFICATIONS_INTERVAL).notify_about_last()
        t = threading.Timer(time_service.to_minutes(config.NOTIFICATIONS_INTERVAL), self.run_)
        t.start()
