from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from app.database import async_session
from app.keyboards.driver_inline import (
    registered_driver_menu_kb,
    unregistered_driver_kb,
)
from app.database.queries import get_driver_by_id

driver_router = Router(name="driver_menu")

@driver_router.callback_query(F.data == "driver_menu")
async def show_driver_menu(cb: CallbackQuery):
    user_id = cb.from_user.id

    async with async_session() as session:
        driver = await get_driver_by_id(session, user_id)

    if driver:
        text = (
            "🚖 <b>Haydovchi bo‘limi</b>\n\n"
            "Kerakli bo‘limni tanlang:"
        )
        await cb.message.edit_text(
            text=text,
            reply_markup=registered_driver_menu_kb(),
            parse_mode=ParseMode.HTML
        )
    else:
        text = (
            "🚗 <b>Haydovchi sifatida ishlashni xohlaysizmi?</b>\n\n"
            "Bizning <b>yopiq haydovchilar guruhimiz</b>ga qo‘shiling va:\n\n"
            "✅ <b>Kuniga 100+ ta real buyurtma</b> qabul qiling\n"
            "💬 Faqat <b>haqiqiy mijozlar</b> — spam va ortiqcha reklamalarsiz\n"
            "💸 <b>Daromadingizni oshiring</b> — yo‘lovchilar bilan to‘g‘ridan-to‘g‘ri bog‘laning\n"
            "🛠 Qo‘shilish uchun <b>ro‘yxatdan o‘ting</b> va rasmiy haydovchilar safidan joy oling\n\n"
            "<b>XIZMAT MUTLAQO BEPUL</b>"
        )

        await cb.message.edit_text(
            text=text,
            reply_markup=unregistered_driver_kb(),
            parse_mode=ParseMode.HTML
        )