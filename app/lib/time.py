from datetime import datetime
from zoneinfo import ZoneInfo

def now_tashkent() -> datetime:
    return datetime.now(ZoneInfo("Asia/Tashkent")).replace(tzinfo=None)
