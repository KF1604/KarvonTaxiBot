from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN

# ─── Bot va Dispatcher ────────────────────────────────────────────────────────
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# ─── Routerlarni ulash ────────────────────────────────────────────────────────
from app.handlers import start, client, driver, admin, common
from app.keyboards import depart_inline
from app.utils import fallback

routers = [
    start.menu_router,
    client.client_router,
    driver.driver_router,
    admin.admin_router,
    common.contact_admin_router,
    depart_inline.router,
    fallback.router
]

for router in routers:
    dp.include_router(router)