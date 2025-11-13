from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.data.viloyatlar import VILOYATLAR2


def registered_driver_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📢 E'lon berish", callback_data="driver_announce")],
        [InlineKeyboardButton(text="👤 Shaxsiy kabinet", callback_data="driver_profile")],
        [InlineKeyboardButton(text="🎥 Videoqo'llanma", callback_data="video_driver")],
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def unregistered_driver_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💬 Admin bilan bog‘lanish", url="t.me/KarvonTaxi_admin")],
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

#----E'lon berish bosqichidagi tugmalar------------
def driver_direction_select_kb(viloyatlar: list = VILOYATLAR2, exclude: str | None = None) -> InlineKeyboardMarkup:
    viloyatlar = [v for v in viloyatlar if v != exclude]

    rows = []
    for i in range(0, len(viloyatlar), 2):
        row = [
            InlineKeyboardButton(text=viloyatlar[i], callback_data=f"vil_{viloyatlar[i]}")
        ]
        if i + 1 < len(viloyatlar):
            row.append(InlineKeyboardButton(text=viloyatlar[i + 1], callback_data=f"vil_{viloyatlar[i + 1]}"))
        rows.append(row)

    rows.append([
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def announcement_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_announcement")],
        [InlineKeyboardButton(text="❌ Qayta kiritish", callback_data="retry_announcement")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="to_main_menu")]
    ])

def confirm_driver_announce_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yuborish", callback_data="send_driver_announce")],
        [InlineKeyboardButton(text="📝 Tahrirlash", callback_data="driver_announce")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def announce_sent_success_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
    ])

#-----Shaxsiy kabinet bosqichidagi tugmalar--------------------
def driver_profile_options_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📞 Telefon raqamni o‘zgartirish", callback_data="edit_driver_phone")],
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="driver_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def driver_profile_options_kb2() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📞 Telefon raqamni o‘zgartirish", callback_data="edit_phone")],
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def driver_phone_confirm_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_driver_phone")],
        [InlineKeyboardButton(text="❌ Xato, qayta kiritish", callback_data="retry_driver_phone")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def to_main_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]]
    )

def stop_announce_button(ann_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="❌ E’lonni to‘xtatish",
                callback_data=f"stop_announce:{ann_id}"
            )]
        ]
    )

def confirm_stop_announce_buttons(announcement_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, to‘xtatish",
                    callback_data=f"admin_confirm_stop:{announcement_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="admin_cancel_stop"
                ),
            ]
        ]
    )