from sqlalchemy import select
from aiogram import Bot
from app.database import async_session
from app.database.models import Announcement
from app.utils.announce_scheduler import start_announcement_task  # siz yozgan faylga qarab

async def restore_announcements(bot: Bot):
    """Bot ishga tushganda faol e’lonlarni qayta tiklaydi"""
    async with async_session() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.is_active == True)
        )
        active_announcements = result.scalars().all()

        for ann in active_announcements:
            start_announcement_task(bot, ann.id)
            print(f"[Announce] Tiklandi: {ann.id} ({ann.from_vil} → {ann.to_vil})")
