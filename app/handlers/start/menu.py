from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart, StateFilter
from aiogram.enums.chat_type import ChatType
from aiogram.fsm.context import FSMContext
from app.keyboards.driver_inline import driver_profile_options_kb2
from app.keyboards.driver_reply import phone_request_kb
from app.states.common_states import PhoneNumberState
from app.database.queries import get_user_by_id, save_user, update_user_phone
from app.keyboards.depart_inline import start_menu_buttons
from app.keyboards.admin_inline import contact_admin_direct
from app.utils.common import send_prompt
from aiogram.types import ReplyKeyboardRemove
from app.utils.helpers import normalize_phone
from app.states.driver_states import PhoneNumberState
from app.database.models import User

router = Router()

# 🔒 Bloklangan foydalanuvchini tekshirish
async def deny_if_blocked(user_id: int, obj) -> bool:
    db_user = await get_user_by_id(user_id)
    if db_user and db_user.is_blocked:
        msg = (
            "🚫 Botdan foydalanish uchun sizga cheklov o‘rnatilgan\n\n"
            "Cheklovni olib tashlash uchun admin bilan bog‘laning"
        )
        if isinstance(obj, Message):
            await obj.answer(msg, reply_markup=contact_admin_direct())
        elif isinstance(obj, CallbackQuery):
            await obj.message.edit_text(msg, reply_markup=contact_admin_direct())
            await obj.answer()
        return True
    return False

# 📲 Telefon raqamini so‘rash uchun tugma
def request_phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# 🔰 /start komandasi
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        bot_username = (await message.bot.get_me()).username
        return await message.answer(
            "🤖 Botdan to‘liq foydalanish uchun tugmani bosing",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🚀 Botga o‘tish", url=f"https://t.me/{bot_username}")]
                ]
            ),
            disable_web_page_preview=True
        )

    user = message.from_user
    user_id = user.id

    db_user = await get_user_by_id(user_id)

    if not db_user:
        await save_user(
            user_id=user_id,
            user_fullname=user.full_name,
            username=user.username or "",
            phone_number=""
        )
        await message.answer(
            f"Assalomu alaykum, <b>{user.full_name}</b>! 👋\n\n"
            "<b>Karvon Taxi</b> botiga xush kelibsiz! 🎉",
            parse_mode="HTML"
        )
        await state.set_state(PhoneNumberState.waiting_for_phone)
        return await message.answer(
            "📱 Botdan to‘liq foydalanish uchun telefon raqamingizni yuboring",
            reply_markup=request_phone_kb()
        )

    if not db_user.phone_number:
        await state.set_state(PhoneNumberState.waiting_for_phone)
        return await message.answer(
            "⚠️ Telefon raqamingizni yubormagansiz\n\n"
            "Botdan to‘liq foydalanish uchun telefon raqamingizni yuboring",
            reply_markup=request_phone_kb()
        )

    if await deny_if_blocked(user_id, message):
        return

    await state.clear()
    is_admin = db_user.role in ["owner", "super_admin", "admin"]

    await send_prompt(
        obj=message,
        state=state,
        text="<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=start_menu_buttons(is_admin=is_admin)
    )

# ☎️ Telefon raqamni qabul qilish (yangi foydalanuvchi yoki tahrir holati)
@router.message(StateFilter(PhoneNumberState.waiting_for_phone))
async def handle_phone_number(msg: Message, state: FSMContext):
    if not msg.contact or msg.contact.user_id != msg.from_user.id:
        await msg.answer("❗️ Iltimos, faqat pastdagi tugmadan foydalaning")
        return

    phone = normalize_phone(msg.contact.phone_number)
    if not phone:
        await msg.answer("<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
            "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>",
                         parse_mode="HTML")
        return

    await update_user_phone(msg.from_user.id, phone)
    await msg.answer("✅ Telefon raqamingiz qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    await state.clear()

    db_user = await get_user_by_id(msg.from_user.id)
    is_admin = db_user.role in ["owner", "super_admin", "admin"]

    await send_prompt(
        obj=msg,
        state=state,
        text="<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=start_menu_buttons(is_admin=is_admin)
    )

# 🔁 Callback orqali asosiy menyu
@router.callback_query(F.data.in_(["main_menu", "cancel_order"]))
async def cb_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if await deny_if_blocked(call.from_user.id, call):
        return

    db_user = await get_user_by_id(call.from_user.id)
    is_admin = db_user.role in ["owner", "super_admin", "admin"]

    await call.message.edit_text(
        "<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=start_menu_buttons(is_admin=is_admin),
        parse_mode="HTML"
    )
    await call.answer()

# 🔁 Matn orqali asosiy menyu
@router.message(F.text.in_(["❌ Bekor qilish", "🏠 Asosiy menyu"]))
async def msg_main_menu(message: Message, state: FSMContext):
    await state.clear()
    if await deny_if_blocked(message.from_user.id, message):
        return

    db_user = await get_user_by_id(message.from_user.id)
    is_admin = False
    if db_user and db_user.role in ["owner", "super_admin", "admin"]:
        is_admin = True
    await message.answer("❌ Bekor qlindi...",reply_markup=ReplyKeyboardRemove())
    await send_prompt(
        obj=message,
        state=state,
        text="<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=start_menu_buttons(is_admin=is_admin)
    )

@router.callback_query(F.data == "user_profile")
async def open_user_profile(call: CallbackQuery):
    db_user : User =  await get_user_by_id(call.from_user.id)

    joined_at_str = db_user.joined_at.strftime('%d.%m.%Y')

    text = (
        "👤 <b>Shaxsiy kabinet</b>\n\n"
        f"<b>👤 Foydalanuvchi:</b> {db_user.user_fullname}\n"
        f"<b>📞 Telefon raqam:</b> {db_user.phone_number or 'Yo‘q'}\n"
        f"<b>🗓 Qo‘shilgan sana:</b> {joined_at_str}"
    )
    await call.message.edit_text(text, reply_markup=driver_profile_options_kb2(), parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data == "edit_phone")
async def edit_phone_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(PhoneNumberState.editing_phone)
    await call.message.edit_text(
        "📲 Yangi telefon raqamingizni yuboring",
        parse_mode="HTML"
    )
    await call.message.answer("⤵️ Telefon raqamni tugma orqali yuboring", reply_markup=phone_request_kb())
    await call.answer()

@router.message(PhoneNumberState.editing_phone)
async def handle_phone_number(msg: Message, state: FSMContext):
    if not msg.contact:
        await msg.answer("⚠️ Faqatgina tugmadan foydalaning")
        return

    if msg.contact.user_id != msg.from_user.id:
        await msg.answer("⚠️ Faqat o‘zingizning raqamingizni yuboring")
        return

    phone = normalize_phone(msg.contact.phone_number)
    if not phone:
        await msg.answer("<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
            "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>", parse_mode="HTML")
        return

    db_user = await get_user_by_id(msg.from_user.id)

    # 🔄 Eski raqam bilan solishtirish
    if db_user.phone_number == phone:
        await msg.answer("⚠️ Ushbu raqam allaqachon hisobingizga ulangan!", reply_markup=ReplyKeyboardRemove())
        await state.clear()

        is_admin = db_user.role in ["owner", "super_admin", "admin"]
        await send_prompt(
            obj=msg,
            state=state,
            text="<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
            reply_markup=start_menu_buttons(is_admin=is_admin)
        )
        return

    await update_user_phone(msg.from_user.id, phone)
    await msg.answer("✅ Telefon raqamingiz yangilandi", reply_markup=ReplyKeyboardRemove())
    await state.clear()

    db_user = await get_user_by_id(msg.from_user.id)
    is_admin = db_user.role in ["owner", "super_admin", "admin"]

    await send_prompt(
        obj=msg,
        state=state,
        text="<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=start_menu_buttons(is_admin=is_admin)
    )

# ❗️ Notug‘ri matn yuborilganda
# @router.message(StateFilter(None), F.chat.type == ChatType.PRIVATE)
# async def fallback_main_menu(message: Message):
#     await message.answer(
#         "❌ <b>Noto‘g‘ri amal</b>\n\nFaqat tugmalardan foydalaning!",
#         parse_mode="HTML"
#     )

# 🚫 Telefon raqam kutilayotgan paytda boshqa hech qanday amalga ruxsat berilmaydi
@router.message(PhoneNumberState.waiting_for_phone)
async def block_actions_until_phone(msg: Message):
    await msg.answer("❗️ Iltimos, avval telefon raqamingizni yuboring\n\n"
                     "📲 Pastdagi tugmadan foydalaning", reply_markup=request_phone_kb())