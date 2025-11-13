from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter, or_f, BaseFilter
from aiogram.enums.parse_mode import ParseMode
from app.states.common_states import ContactAdminState
from app.states.depart_states import OrderState
from app.states.parcel_states import ParcelState
from app.keyboards.depart_inline import to_main_menu_inline
from app.keyboards.depart_reply import cancel_reply_kb

router = Router(name="fallback")

#─── Faqat inline tugma kerak bo‘lgan holatlar ─────────────────────────────
INLINE_ONLY_STATES = [
    OrderState.choose_from_viloyat,
    OrderState.choose_from_tuman,
    OrderState.choose_to_viloyat,
    OrderState.choose_to_tuman,
    OrderState.confirm,
]

@router.message(StateFilter(*INLINE_ONLY_STATES), ~F.text.in_([
    "🏠 Asosiy menyu", "❌ Bekor qilish"
]))
async def fallback_inline_only(message: Message):
    await message.answer(
        "❌ <b>Noto‘g‘ri amal</b>\n\nFaqat tugmalardan foydalaning!",
        parse_mode=ParseMode.HTML
    )

#------Parcel bosqichi uchun fallbacklar--------------------------------------
INLINE_ONLY_STATES = [
    ParcelState.choose_from_viloyat,
    ParcelState.choose_from_tuman,
    ParcelState.choose_to_viloyat,
    ParcelState.choose_to_tuman,
    ParcelState.confirm,
]

@router.message(StateFilter(*INLINE_ONLY_STATES), ~F.text.in_([
    "🏠 Asosiy menyu", "❌ Bekor qilish"
]))
async def fallback_inline_only(message: Message):
    await message.answer(
        "❌ <b>Noto‘g‘ri amal</b>\n\nFaqat tugmalardan foydalaning!",
        parse_mode=ParseMode.HTML
    )

# ─── Matn bo‘lmagan xabarlarni aniqlovchi filter ──────────────────────────
class IsNotText(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        return msg.text is None

class IsReply(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        return bool(msg.reply_to_message)

# ─── Mijoz contact_admin holatida noto‘g‘ri xabar yuborsa ─────────────────
@router.message(ContactAdminState.writing, or_f(IsNotText(), IsReply()))
async def fallback_user(msg: Message):
    await msg.answer(
        "⚠️ Faqat matnli xabar yuborish mumkin\n\n"
        "✍️ Taklif, savol yoki shikoyatingizni matn shaklida yozing",
        reply_markup=cancel_reply_kb()
    )

# ─── Admin contact_admin javob holatida noto‘g‘ri xabar yuborsa ──────────
@router.message(ContactAdminState.admin_answer, or_f(IsNotText(), IsReply()))
async def fallback_admin(msg: Message):
    await msg.answer(
        "⚠️ Faqat matnli javob yuborishingiz mumkin\n\n"
        "✍️ Javobni matn ko‘rinishida yuboring yoki “Bekor qilish” tugmasini bosing",
        reply_markup=cancel_reply_kb()
    )

# ─── Muloqot tugaganidan keyingi fallback (agar kerak bo‘lsa) ─────────────
@router.message(ContactAdminState.awaiting_menu, or_f(IsNotText(), IsReply(), F.text))
async def fallback_awaiting(msg: Message):
    await msg.answer(
        "❌ Sizning xabaringiz qabul qilinmadi\n\n"
        "Oldingi murojaatingiz allaqachon adminga yuborilgan\n\n"
        "🏠 Asosiy menyuga qaytib, kerakli bo‘limni tanlang",
        reply_markup=to_main_menu_inline(),  # ← agar siz uni argument bilan yozmagan bo‘lsangiz
        parse_mode=ParseMode.HTML
    )