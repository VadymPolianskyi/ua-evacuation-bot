import re
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

UA_TZ = "Europe/Kiev"


def now() -> datetime:
    return _now(UA_TZ)


def _now(tz: str = None) -> datetime:
    return datetime.now(tz=ZoneInfo(tz)) if tz else datetime.now()


def to_tz(t: datetime, tz: str):
    return t.astimezone(tz=ZoneInfo(tz))


def extract_from_time(time_str: str) -> Optional[datetime]:
    m = re.search(r'(\d+:\d+)', time_str)

    if not m:
        return None
    else:
        hours, minutes = tuple(m.group(1).split(':'))
        dt = now()
        return dt.replace(hour=int(hours), minute=int(minutes))


def extract_datetime(date_time_str: str) -> Optional[datetime]:
    try:
        extracted = datetime.strptime(date_time_str, '%d-%m-%Y %H:%M')
    except ValueError:
        print(f"Error when converting '{date_time_str}' to datetime")
        extracted = extract_from_time(date_time_str)

    return extracted


def validate(tm: datetime) -> bool:
    return to_tz(tm, UA_TZ) >= now()
