from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ─── Admin uchun CallbackData ────────────────────────────────────────────────
class FB(CallbackData, prefix="fb"):
    action: str        # reply / cancel
    fid: int           # feedback_id

# ─── Foydalanuvchi uchun: Admin javobidan so‘ng chiqadigan tugmalar ──────────
def user_reply_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✍️ Javob yozish", callback_data="contact_admin")
        ]
    ])

# ─── Foydalanuvchi uchun: faqat “Asosiy menyu” tugmasi ───────────────────────
def to_main_menu_inline(user_id: int = None) -> InlineKeyboardMarkup:
    # user_id kerak bo‘lsa, shart orqali menu o‘zgartiriladi
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
    ]])

def admin_act_inline(feedback_id: int) -> InlineKeyboardMarkup:
    """
    Admin xabariga biriktiriladigan tugmalar:
      ✍️ Javob yozish
      👤 Akkaunt – public bo‘lsa URL, privat bo‘lsa callback
    """
    buttons = [
        InlineKeyboardButton(
            text="✍️ Javob yozish",
            callback_data=FB(action="reply", fid=feedback_id).pack()
        )
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])