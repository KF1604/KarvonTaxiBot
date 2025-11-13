from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from app.keyboards.admin_inline import admin_menu_buttons
from app.database.queries import get_user_by_id

router = Router(name="admin_panel")

# ─── Admin panelga kirish ─────────────────────────────────────
@router.callback_query(F.data == "admin_panel")
async def enter_admin_panel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    db_user = await get_user_by_id(cb.from_user.id)
    if not db_user:
        await cb.answer("⚠️ Siz ro‘yxatdan o‘tmagansiz.", show_alert=True)
        return

    await cb.message.edit_text(
        "<b>🔐 Admin panel</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=admin_menu_buttons(db_user.role),
        parse_mode=ParseMode.HTML
    )
    await cb.answer()