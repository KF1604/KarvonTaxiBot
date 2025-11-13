from aiogram import Router
from .menu import driver_router as menu_router
from .announce import router as announce_router
from .profile import driver_router as profile_router

driver_router = Router(name="driver")

driver_router.include_routers(
    menu_router,
    announce_router,
    profile_router,
)