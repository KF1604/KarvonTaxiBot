from aiogram import Router
from .admin_panel import router as admin_panel_router
from .admins import router as admins_router
from .drivers import router as drivers_router
from .users import router as users_router
from .ads import router as ads_router
from .stats import router as stats_router
from .bot_mode import router as bot_mode_router
from .sending_payment import router as sending
from .video_help import router as video_helps

admin_router = Router(name="admin")

admin_router.include_routers(
    admin_panel_router,
    admins_router,
    drivers_router,
    users_router,
    ads_router,
    stats_router,
    bot_mode_router,
    sending,
    video_helps
)