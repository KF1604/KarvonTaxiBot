from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# def phone_keyboard() -> ReplyKeyboardMarkup:
#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
#             [KeyboardButton(text="❌ Bekor qilish")]
#         ],
#         resize_keyboard=True
#     )

def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Telefon raqamni yozing..."
    )

def location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Geo-joylashuvni yuborish", request_location=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

def comment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭️ O‘tkazib yuborish")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Izoh yozish..."
    )

# Foydalanuvchi va admin uchun bir xil “Bekor qilish”
def cancel_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Matn yuboring yoki “Bekor qilish”ni bosing",
    )