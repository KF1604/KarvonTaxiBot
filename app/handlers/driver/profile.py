from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext

from app.database.session import async_session
from app.database.queries import get_driver_by_id, update_driver_phone, get_setting_value
from app.keyboards import to_main_menu_inline
from app.keyboards.driver_inline import driver_profile_options_kb, driver_phone_confirm_kb, registered_driver_menu_kb
from app.keyboards.driver_reply import phone_request_kb, cancel_reply_kb, send_phone_again_kb
from app.states.driver_states import DriverPhoneState
from app.utils.helpers import normalize_phone

driver_router = Router(name="driver_profile")

@driver_router.callback_query(F.data == "driver_profile")
async def show_driver_profile(cb: CallbackQuery):
    async with async_session() as session:
        driver = await get_driver_by_id(session, cb.from_user.id)
        bot_mode = await get_setting_value(session, "bot_mode")

    if not driver:
        await cb.answer("❌ Siz ro‘yxatdan o‘tmagansiz", show_alert=True)
        return

    # Asosiy ma'lumotlar
    text = (
        f"<b>👤 Shaxsiy kabinet</b>\n\n"
        f"<b>👤 Ism:</b> {driver.fullname}\n"
        f"<b>📞 Telefon:</b> {driver.phone_number or 'Kiritilmagan'}\n"
        f"<b>🚘 Avtomobil rusumi:</b> {driver.car_model}\n"
        f"<b>🔢 Davlat raqami:</b> {driver.car_number}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {driver.joined_at.strftime('%d.%m.%Y')}"
    )

    # Faqat pullik rejim bo‘lsa, pullik ma'lumotlar qo‘shiladi
    if str(bot_mode).lower() == "paid":
        text += (
            f"\n<b>💰 To‘lov holati:</b> {'✅ To‘langan' if driver.is_paid else '❌ To‘lanmagan'}"
        )
        if driver.paid_until:
            text += f"\n<b>📆 Obuna muddati:</b> {driver.paid_until.strftime('%d.%m.%Y | %H:%M gacha')}"
        else:
            text += f"\n<b>📆 Obuna muddati:</b> belgilanmagan"

    await cb.message.edit_text(
        text=text,
        reply_markup=driver_profile_options_kb(),
        parse_mode=ParseMode.HTML
    )

@driver_router.callback_query(F.data == "edit_driver_phone")
async def prompt_phone_edit(cb: CallbackQuery, state: FSMContext):
    await state.set_state(DriverPhoneState.editing_phone)
    await cb.message.delete()
    await cb.message.answer(
        "📲 Raqamni o‘zgartirish uchun pastdagi 'Telefon raqamni yuborish' tugmasini bosing",
        reply_markup=phone_request_kb(),
        parse_mode=ParseMode.HTML
    )

@driver_router.message(DriverPhoneState.editing_phone, F.contact)
async def process_driver_contact(msg: Message, state: FSMContext):
    if msg.contact.user_id != msg.from_user.id:
        await msg.answer("❌ Faqat o‘zingizning raqamingizni yuboring", reply_markup=cancel_reply_kb())
        return

    phone = normalize_phone(msg.contact.phone_number)

    if not phone:
        await msg.answer(
            "<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
            "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>",
            reply_markup=send_phone_again_kb()
        )
        return

    async with async_session() as session:
        driver = await get_driver_by_id(session, msg.from_user.id)

    if driver.phone_number == phone:
        await msg.answer(
            "⚠️ Ushbu raqam allaqachon hisobingizga ulangan!",
            reply_markup=ReplyKeyboardRemove()
        )

        text = (
            "🚖 <b>Haydovchi bo‘limi</b>\n\n"
            "Kerakli bo‘limni tanlang:"
        )
        await msg.answer(text, reply_markup=registered_driver_menu_kb(), parse_mode=ParseMode.HTML)
        return

    await state.update_data(phone=phone)

    text = (
        "<b>📲 Telefon raqamingizni tasdiqlang:</b>\n\n"
        f"<b>Ism:</b> {driver.fullname}\n"
        f"<b>Telefon:</b> {phone}"
    )
    await state.set_state(DriverPhoneState.confirming_phone)
    await msg.answer(text, parse_mode=ParseMode.HTML, reply_markup=driver_phone_confirm_kb())

@driver_router.message(DriverPhoneState.editing_phone)
async def block_manual_phone_entry(msg: Message):
    await msg.answer("❌ Raqamni faqat <b>Telefon raqamni yuborish</b> tugmasi orqali jo‘nating", parse_mode=ParseMode.HTML, reply_markup=phone_request_kb())

@driver_router.callback_query(F.data == "confirm_driver_phone")
async def confirm_driver_phone(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    await update_driver_phone(cb.from_user.id, phone)
    await state.clear()

    await cb.message.edit_text(
        "✅ Telefon raqamingiz muvaffaqiyatli o‘zgartirildi!",
        reply_markup=to_main_menu_inline()
    )

@driver_router.callback_query(F.data == "retry_driver_phone")
async def retry_driver_phone(cb: CallbackQuery, state: FSMContext):
    await state.set_state(DriverPhoneState.editing_phone)
    await cb.message.delete()
    await cb.message.answer(
        "📲 Raqamni o‘zgartirish uchun pastdagi 'Telefon raqamni yuborish' tugmasini bosing",
        reply_markup=phone_request_kb()
    )