from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def order_for_whom_buttons2():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙋‍♂️ O'zim", callback_data="order_for_me")],
        [InlineKeyboardButton(text="👤 Tanishim", callback_data="order_for_friend")],
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="start_mijoz")]
    ])

def viloyat_buttons(viloyatlar: list) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(viloyatlar), 2):
        row = []
        for j in range(2):
            if i + j < len(viloyatlar):
                row.append(InlineKeyboardButton(text=viloyatlar[i + j], callback_data=f"viloyat_{viloyatlar[i + j]}"))
        rows.append(row)
    rows.append([

        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def tuman_buttons(tumanlar: list) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(tumanlar), 2):
        row = []
        for j in range(2):
            if i + j < len(tumanlar):
                row.append(InlineKeyboardButton(text=tumanlar[i + j], callback_data=f"tuman_{tumanlar[i + j]}"))
        rows.append(row)
    rows.append([
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Barchasi to‘g‘ri, tasdiqlayman", callback_data="confirm_order")],
        [InlineKeyboardButton(text="🔄 Xato, qayta kiritaman", callback_data="order_parcel")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="main_menu")]
    ])

def to_main_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]]
    )

def contact_client_button(user_id: int, username: str | None = None) -> InlineKeyboardMarkup:
    if username:
        btn = InlineKeyboardButton(
            text="👉 Mijozga yozish 👈", url=f"tg://user?id={user_id}"
        )
    else:
        btn = InlineKeyboardButton(
            text="👉 Mijozga yozish 👈", callback_data=f"write_to_user:{user_id}"
        )
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])