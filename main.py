import asyncio
import logging
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.bot import DefaultBotProperties
from config import API_TOKEN
from dispatcher import dp
from app.database.session import create_db
from app.utils.scheduler import setup_scheduler, scheduler
from app.utils.announcement import restore_announcements
# hello
async def setup_bot(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Foydalanishni boshlash"),
    ])

async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=API_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await create_db()
    await setup_bot(bot)

    await setup_scheduler(bot)
    scheduler.start()

    await restore_announcements(bot)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# main.py
# import asyncio
# import logging
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
#
# from app.utils.userbot_manager import start_userbot  # Telethon userbot
# from dispatcher import dp
# from config import API_TOKEN
#
# # Logging sozlamasi
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
# )
# logger = logging.getLogger(__name__)
#
# # ✅ Yangi formatda bot obyektini yaratamiz
# bot = Bot(
#     token=API_TOKEN,
#     default=DefaultBotProperties(parse_mode="HTML")
# )
#
# dispatcher = Dispatcher()
#
#
# async def start_aiogram_bot():
#     """Aiogram botni ishga tushirish."""
#     logger.info("🚀 Aiogram bot ishga tushdi...")
#     await dp.start_polling(bot)
#
#
# async def main():
#     """Asosiy ishga tushirish nuqtasi."""
#     # Telethon userbotni fon jarayon sifatida ishga tushiramiz
#     asyncio.create_task(start_userbot())
#
#     # Aiogram botni ishga tushiramiz
#     await start_aiogram_bot()
#
#
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except (KeyboardInterrupt, SystemExit):
#         logger.warning("🛑 Bot to‘xtatildi.")