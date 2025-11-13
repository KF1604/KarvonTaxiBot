from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Foydalanuvchi va admin uchun bir xil “Bekor qilish”
def cancel_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Matn yuboring yoki “Bekor qilish”ni bosing",
    )