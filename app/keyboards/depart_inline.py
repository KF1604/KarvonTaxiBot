from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def start_menu_buttons(is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🙋‍♂️ Yo'lovchiman", callback_data="start_mijoz"),
            InlineKeyboardButton(text="🚖 Haydovchiman", callback_data="driver_menu"),
        ],
        [
            InlineKeyboardButton(text="👤 Shaxsiy kabinet", callback_data="user_profile")
        ],
        [
            InlineKeyboardButton(text="🎥 Videoqo'llanma", callback_data="video_client")
        ]
    ]
    if is_admin:
        buttons.append(
            [InlineKeyboardButton(text="🔐 Admin bo‘limi", callback_data="admin_panel")]
        )
    else:
        buttons.append(
            [InlineKeyboardButton(text="💬 Admin bilan bog‘lanish", callback_data="contact_admin")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def order_type_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚖 Jo‘nab ketish", callback_data="order_depart")],
        [InlineKeyboardButton(text="📦 Jo‘natma yuborish", callback_data="order_parcel")],
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="main_menu")]
    ])

def order_for_whom_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙋‍♂️ O‘zim uchun", callback_data="order_for_me")],
        [InlineKeyboardButton(text="👤 Tanishim uchun", callback_data="order_for_friend")],
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
        [InlineKeyboardButton(text="🔄 Xato, qayta kiritaman", callback_data="order_depart")],
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


from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hlink
from aiogram.exceptions import TelegramBadRequest
from app.database.queries import get_driver_by_id1

router = Router()

@router.callback_query(F.data.startswith("write_to_user:"))
async def handle_write_to_user(call: CallbackQuery):
    """
    Username bo‘lmagan mijozga haydovchi tugmani bosganda:
    - Mijozga bot orqali xabar yuboriladi
    - Haydovchiga esa alert chiqadi
    """
    client_id = int(call.data.split(":")[1])
    driver = call.from_user
    driver_db = await get_driver_by_id1(driver.id)  # 🔍 DBdan haydovchi ma’lumotlarini olamiz

    # 🔽 Haydovchini ko‘rsatish — username bo‘lsa @username, yo‘q bo‘lsa telefon
    if driver.username:
        driver_ref = f"@{driver.username}"
    elif driver_db and driver_db.phone_number:
        driver_ref = f"<b>📞 {driver_db.phone_number}</b>"
    else:
        driver_ref = hlink(driver.full_name, f"tg://user?id={driver.id}")

    try:
        await call.bot.send_message(
            chat_id=client_id,
            text=(
                "🚖 <b>Haydovchi siz bilan bog‘lanmoqchi!</b>\n\n"
                f"{driver_ref} sizga yozishga harakat qildi, lekin akkauntingiz yopiq bo‘lgani uchun bog‘lana olmadi\n\n"
                "Iltimos, unga birinchi bo‘lib o‘zingiz yozing"
            ),
            parse_mode="HTML"
        )

        await call.answer(
            "ℹ️ Akkaunt yopiq\n\n"
            "Mijoz akkaunti yopiq bo‘lgani uchun siz bevosita yozolmaysiz\n\n"
            "✅ Mijozga xabar yuborildi, javobini kuting",
            show_alert=True
        )

    except TelegramBadRequest:
        await call.answer(
            "❌ Mijozga yozib bo‘lmadi. Ehtimol, u botni bloklagan.",
            show_alert=True
        )