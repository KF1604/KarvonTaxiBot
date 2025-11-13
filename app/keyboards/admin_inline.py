from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def contact_admin_direct() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Admin bilan bog‘lanish", callback_data="contact_admin")]
        ]
    )

# ─── Admin menyusi ─────────────────────────────────────────────
def admin_menu_buttons(role: str) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if role == "owner":
        buttons += [
            [InlineKeyboardButton(text="👮 Adminlar", callback_data="admin_manage")],
            [InlineKeyboardButton(text="🚗 Haydovchilar", callback_data="driver_manage")],
            [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="manage_users")],
            [InlineKeyboardButton(text="📢 E’lon/reklama yuborish", callback_data="send_ads")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="statistics")],
            [InlineKeyboardButton(text="🤖 Bot rejimi", callback_data="bot_mode")],  # ✅ Faqat owner uchun
        ]
    elif role == "super_admin":
        buttons += [
            [InlineKeyboardButton(text="👮 Adminlar", callback_data="admin_manage")],
            [InlineKeyboardButton(text="🚗 Haydovchilar", callback_data="driver_manage")],
            [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="manage_users")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="statistics")],
        ]
    elif role == "admin":
        buttons += [
            [InlineKeyboardButton(text="🚗 Haydovchilar", callback_data="driver_manage")],
            [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="manage_users")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="statistics")],
        ]

    buttons.append([InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── Admin bo‘limi menyusi ─────────────────────────────────────
def admin_manage_buttons(role: str) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if role in ("owner", "super_admin"):
        buttons.append([
            InlineKeyboardButton(text="➕ Admin qo‘shish", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Admin o‘chirish", callback_data="remove_admin")
        ])

    if role == "owner":
        buttons.append([
            InlineKeyboardButton(text="✏️ Rolni o‘zgartirish", callback_data="change_admin_role")
        ])

    buttons.append([InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data="list_admins")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="admin_panel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_role_buttons(current_role: str) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if current_role == "owner":
        buttons.append([InlineKeyboardButton(text="👑 Super admin", callback_data="super_admin")])

    buttons.append([InlineKeyboardButton(text="👤 Oddiy admin", callback_data="admin")])
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_add")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

#-------Yangi admin qo'shish uchun tasdiqlash tugmalari--------------
def confirm_admin_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_add"),
            InlineKeyboardButton(text="🔁 Qayta kiritish", callback_data="retry_add")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_add")]
    ])

#--------Adminni o'chirish uchun tasdiqlash tugmalari-------------------
def confirm_remove_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_rm"),
            InlineKeyboardButton(text="🔁 Qayta kiritish", callback_data="retry_rm")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_rm")]
    ])

#------Asosiy menyuga qaytish uchun tugma-----------
def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
    ])

#--------Ortga qaytish uchun tugma--------------
def kb_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="admin_manage")]
    ])

# ─── Xatolikdan keyin ortga qaytish ───────────────────────────
def retry_back_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="retry_rm")]
    ])

#-----HAYDOVCHILAR QISMI------------

# ─── Haydovchilar bo‘limi menyusi ─────────────────────────────────
def drivers_menu_buttons(role: str) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if role in ["super_admin", "owner"]:
        buttons.append([InlineKeyboardButton(text="➕ Haydovchi qo‘shish", callback_data="add_driver")])
        buttons.append([InlineKeyboardButton(text="🗑 Haydovchini o‘chirish", callback_data="remove_driver")])
        buttons.append([InlineKeyboardButton(text="➕ Guruh ID qo‘shish", callback_data="add_group_id")])
        buttons.append([InlineKeyboardButton(text="➖ Guruh ID o‘chirish", callback_data="remove_group_id")])
        buttons.append([InlineKeyboardButton(text="✏️ Telefon raqamini tahrirlash", callback_data="edit_driver_phone2")])
        buttons.append([InlineKeyboardButton(text="🚘 Mashina rusumini tahrirlash", callback_data="edit_car_model")])
        buttons.append([InlineKeyboardButton(text="🔢 Davlat raqamini tahrirlash", callback_data="edit_car_number")])
        buttons.append([InlineKeyboardButton(text="📊 Statistika", callback_data="driver_stats")])
        buttons.append([InlineKeyboardButton(text="❌ E'lonni to‘xtatish", callback_data="stop_driver_announce")])

    else:
        buttons.append([InlineKeyboardButton(text="➕ Haydovchi qo‘shish", callback_data="add_driver")])
        buttons.append([InlineKeyboardButton(text="➕ Guruh ID qo‘shish", callback_data="add_group_id")])

    buttons.append([InlineKeyboardButton(text="🔍 Haydovchini topish", callback_data="find_driver")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="admin_panel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_back2() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="driver_manage")]
    ])

# ─── Haydovchini tasdiqlash uchun tugmalar ───────────────────────
def confirm_driver_add_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_driver_add")],
        [InlineKeyboardButton(text="🔁 Qayta kiritish", callback_data="retry_driver_add")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_driver_add")]
    ])

# ─── Haydovchini o‘chirish tasdiqlash ─────────────────────────────
def confirm_remove_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o‘chirilsin", callback_data="confirm_rm")],
        [InlineKeyboardButton(text="🔁 Qayta ID kiritish", callback_data="retry_rm")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_rm")]
    ])

# ─── Haydovchini telefon raqamini tahrirlash uchun tasdiqlash ─────────────────────────────
def confirm_driver_edit_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_driver_edit"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_driver_edit")
        ]
    ])

def confirm_car_model_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_car_model")],
        [InlineKeyboardButton(text="🔁 Qayta ID kiritish", callback_data="edit_car_model")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_car_model")]
    ])

def confirm_car_number_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_car_number")],
        [InlineKeyboardButton(text="🔁 Qayta ID kiritish", callback_data="edit_car_number")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_car_number")]
    ])

#--------Foydalanuvchilar qismi uchun tugmalar---------------
def users_menu_buttons(role: str) -> InlineKeyboardMarkup:
    buttons = []

    buttons.append([InlineKeyboardButton(text="🔍 Foydalanuvchini topish", callback_data="find_user")])

    # 🚫 ❌ Bloklash, blokdan chiqarish va o‘chirish faqat owner/super_admin uchun
    if role in ["owner", "super_admin"]:
        buttons.extend([
            [InlineKeyboardButton(text="🚫 Foydalanuvchini bloklash", callback_data="block_user")],
            [InlineKeyboardButton(text="♻️ Foydalanuvchini blokdan chiqarish", callback_data="unblock_user")],
            [InlineKeyboardButton(text="🗑 Foydalanuvchini o‘chirish", callback_data="delete_user")],
        ])

    buttons.append([InlineKeyboardButton(text="✉️ Foydalanuvchiga yozish", callback_data="message_user")])

    buttons.append([InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="admin_panel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_back3() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="manage_users")]
    ])

#---Foydalanuvchini bloklash uchun tugma---------
def confirm_block() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_block")],
        [InlineKeyboardButton(text="🔁 ID qayta kiritish", callback_data="block_user")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="manage_users")]
    ])

def confirm_unblock() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, chiqarilsin", callback_data="confirm_unblock")],
        [InlineKeyboardButton(text="🔁 ID qayta kiritish", callback_data="unblock_user")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="manage_users")]
    ])

def confirm_deleteuser() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chirilsin", callback_data="confirm_delete")],
        [InlineKeyboardButton(text="🔁 ID qayta kiritish", callback_data="delete_user")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="manage_users")]
    ])

#-------Reklama bosqichi uchun tugmalar--------
def confirm_ad_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_ads"),
            InlineKeyboardButton(text="♻️ Qayta yozish", callback_data="retry_ads"),
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_manage"),
        ]
    ])

#-------Statistika uchun tugma---------
def kb_back4() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="admin_panel")],
        ]
    )

#-----Bot rejimi uchun tugma---------
def bot_mode_control_buttons(current_mode: str) -> InlineKeyboardMarkup:
    new_mode = "paid" if current_mode == "free" else "free"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"♻️ Rejimni «{'Pullik' if new_mode == 'paid' else 'Bepul'}» ga o‘zgartirish",
                callback_data="switch_bot_mode"
            )
        ],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="admin_panel")]
    ])

def confirm_bot_mode_change(current_mode: str) -> InlineKeyboardMarkup:
    new_mode = "paid" if current_mode == "free" else "free"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Ha, o‘zgartir",
                callback_data=f"confirm_bot_mode:{new_mode}"
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="admin_panel"
            )
        ]
    ])

