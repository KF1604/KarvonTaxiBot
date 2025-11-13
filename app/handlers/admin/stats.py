from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from datetime import timedelta

from sqlalchemy import select, func
from app.database.session import async_session
from app.database.models import User
from app.keyboards.admin_inline import kb_back4
from app.lib.time import now_tashkent

router = Router(name="admin_stats")

@router.callback_query(F.data == "statistics")
async def show_statistics(cb: CallbackQuery):
    today = now_tashkent().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    async with async_session() as session:
        # Umumiy foydalanuvchilar soni
        total_stmt = select(func.count()).select_from(User)
        total = (await session.execute(total_stmt)).scalar()

        # Bir kunda ro'yxatdan o'tganlar
        day_stmt = select(func.count()).where(func.date(User.joined_at) == today)
        day = (await session.execute(day_stmt)).scalar()

        # Oxirgi 7 kunda ro'yxatdan o'tganlar
        week_stmt = select(func.count()).where(User.joined_at >= week_ago)
        week = (await session.execute(week_stmt)).scalar()

        # Oxirgi 30 kunda ro'yxatdan o'tganlar
        month_stmt = select(func.count()).where(User.joined_at >= month_ago)
        month = (await session.execute(month_stmt)).scalar()

        # Oxirgi 1 yilda ro'yxatdan o'tganlar
        year_stmt = select(func.count()).where(User.joined_at >= year_ago)
        year = (await session.execute(year_stmt)).scalar()

    text = (
        "<b>📊 Yangi foydalanuvchilar:</b>\n\n"
        f"• Bir kunda: <b>{day} ta</b>\n"
        f"• Bir haftada: <b>{week} ta</b>\n"
        f"• Bir oyda: <b>{month} ta</b>\n"
        f"• Bir yilda: <b>{year} ta</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{total} ta</b>"
    )

    await cb.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb_back4())
    await cb.answer()