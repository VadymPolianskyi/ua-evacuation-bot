from src.db.entity import AnnouncementType
from src.service.announcement import AnnouncementService
from src.service.city import CityService
import csv
import logging

a_service = AnnouncementService()
c_service = CityService()

a_header = ["id", "user_id", "a_type", "a_service", "info", "city_from_id", "city_to_id", "scheduled", "created"]
c_header = ["id", "name", "country"]


def backup_announcements(header: list, filename: str):
    logging.info("Start ANNOUNCEMENT backup")
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(header)

        for a in a_service.dao.find_all():
            if a.a_type == AnnouncementType.share:
                logging.info(a.to_str())
                data = [a.id, a.user_id, a.a_type.name, a.a_service.name,
                        a.info.strip(), a.city_from_id, a.city_to_id, a.scheduled, a.created]
                writer.writerow(data)
    logging.info("Finished ANNOUNCEMENT backup")


def backup_city(header: list, filename: str):
    logging.info("Start CITY backup")
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(header)

        for c in c_service.dao.find_all():
            logging.info(c.name)
            data = [c.id, c.name, c.country]
            writer.writerow(data)
    logging.info("Finished CITY backup")


backup_city(c_header, 'evacuation_city.csv')
