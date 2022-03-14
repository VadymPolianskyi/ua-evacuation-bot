import logging
import re
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

UA_TZ = "Europe/Kiev"
UTC_TZ = "UTC"


def now() -> datetime:
    return _now(UA_TZ)


def now_utc() -> datetime:
    return _now(UTC_TZ)


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
        extracted = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
    except ValueError:
        logging.error(f"Error when converting '{date_time_str}' to datetime")
        extracted = extract_from_time(date_time_str)

    return extracted


def validate(tm: datetime) -> bool:
    return to_tz(tm, UA_TZ) >= now()


def minus(dt: datetime, months: int = 0, weeks: int = 0, days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    if months > 0:
        days += months * 30

    return dt - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)


def to_minutes(seconds: int):
    return seconds * 60
