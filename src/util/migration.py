from src.service.announcement import AnnouncementService
from src.service.city import CityService

a_service = AnnouncementService()
c_service = CityService()

for ae in a_service.dao.find_all():
    ae.city_from_id = c_service.find_by_name(ae.city_a).id
    ae.city_to_id = c_service.find_by_name(ae.city_b).id if ae.city_b else None
    a_service.dao.update(ae)
