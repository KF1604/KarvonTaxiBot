from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from app.keyboards.admin_inline import (
    bot_mode_control_buttons,
    confirm_bot_mode_change
)
from app.database.queries import get_bot_mode

router = Router(name="bot_mode")

# 🟢 1. Rejimni ko‘rsatish
@router.callback_query(F.data == "bot_mode")
async def show_bot_mode(cb: CallbackQuery):
    current = await get_bot_mode()
    text = (
        "🤖 Botning joriy rejimi: "
        f"<b>{'Pullik' if current == 'paid' else 'Bepul'}</b>\n\n"
        "Quyidagi tugma orqali rejimni o‘zgartirishingiz mumkin."
    )
    await cb.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=bot_mode_control_buttons(current)
    )

# 🟠 2. O‘zgartirishni tasdiqlashga taklif
@router.callback_query(F.data == "switch_bot_mode")
async def ask_confirmation(cb: CallbackQuery):
    current = await get_bot_mode()
    new_mode = "Pullik" if current == "free" else "Bepul"
    await cb.message.edit_text(
        f"⚠️ Siz botni <b>{new_mode}</b> rejimiga o‘tkazmoqchisiz.\n"
        f"Ishonchingiz komilmi?",
        parse_mode=ParseMode.HTML,
        reply_markup=confirm_bot_mode_change(current)
    )