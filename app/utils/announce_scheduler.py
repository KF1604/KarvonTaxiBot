import asyncio
from typing import Dict
from aiogram import Bot
from app.database import async_session
from app.database.models import Announcement
from app.utils.get_driver_group import get_driver_group_id

# barcha faol tasklarni RAMda saqlaymiz
announcement_tasks: Dict[int, asyncio.Task] = {}

async def send_announcement_periodically(bot: Bot, ann_id: int):
    """Har 5 daqiqada e’lonni guruhga yuborib turadi"""
    while True:
        async with async_session() as session:
            ann = await session.get(Announcement, ann_id)
            if not ann or not ann.is_active:
                break

            group_id = await get_driver_group_id(ann.from_vil, ann.to_vil)
            text = f"<b>{ann.from_vil} → {ann.to_vil}</b>\n\n".upper() + ann.text

            try:
                await bot.send_message(group_id, text, parse_mode="HTML")
            except Exception as e:
                print(f"[Announce] Error sending: {e}")

        await asyncio.sleep(300)  # 5 daqiqa

def start_announcement_task(bot: Bot, ann_id: int):
    """Yangi task yaratish"""
    task = asyncio.create_task(send_announcement_periodically(bot, ann_id))
    announcement_tasks[ann_id] = task

async def stop_announcement_task(ann_id: int):
    """Faol taskni to‘xtatish"""
    task = announcement_tasks.pop(ann_id, None)
    if task:
        task.cancel()

    async with async_session() as session:
        ann = await session.get(Announcement, ann_id)
        if ann:
            ann.is_active = False
            await session.commit()