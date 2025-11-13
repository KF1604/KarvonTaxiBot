from datetime import timedelta
from sqlalchemy import select, desc
from app.database.models import Announcement
from app.database.session import async_session
from app.lib.time import now_tashkent

LIMIT_MINUTES = 5  # daqiqa

async def is_allowed_to_announce(driver_id: int) -> tuple[bool, str | None]:
    now = now_tashkent()
    check_from = now - timedelta(minutes=LIMIT_MINUTES)

    async with async_session() as session:
        result = await session.execute(
            select(Announcement)
            .where(Announcement.driver_id == driver_id)
            .where(Announcement.created_at >= check_from)
            .order_by(desc(Announcement.created_at))
            .limit(1)
        )
        last_announcement = result.scalar_one_or_none()
        if last_announcement is None:
            return True, None

        next_time = (last_announcement.created_at + timedelta(minutes=LIMIT_MINUTES)).strftime("%H:%M")
        return False, next_time