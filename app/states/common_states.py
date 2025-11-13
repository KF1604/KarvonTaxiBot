from aiogram.fsm.state import StatesGroup, State

class ContactAdminState(StatesGroup):
    writing        = State()   # Foydalanuvchi xabar yozmoqda
    awaiting_menu  = State()   # Yuborilgandan so‘ng “Asosiy menyu” tugmasini kutyapti
    admin_answer   = State()   # Admin javob yozmoqda

class PhoneNumberState(StatesGroup):
    waiting_for_phone = State()
