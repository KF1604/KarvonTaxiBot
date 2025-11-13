from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from app.database.session import async_session
from app.database.models import Driver, Setting, Announcement
from app.database.queries import get_user_by_id, get_driver_by_id, deactivate_announcement, \
    get_active_announcement_by_driver
from app.keyboards.driver_inline import confirm_stop_announce_buttons
from app.states.admin_states import AdminManageState
from app.states.driver_states import AdminAnnouncementStates
from app.utils.text_tools import escape_html
from app.utils.helpers import normalize_phone
from app.keyboards.admin_reply import cancel_reply_kb
from app.keyboards.admin_inline import (
    kb_main,
    confirm_driver_add_buttons,
    confirm_remove_buttons,
    confirm_driver_edit_buttons,
    drivers_menu_buttons, kb_back2, confirm_car_model_buttons, confirm_car_number_buttons,
)
from sqlalchemy import select, func, update
from app.lib.time import now_tashkent
from dispatcher import bot
from datetime import timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import GROUPS  # .env dagi ruxsat etilgan guruh ID lar
from app.utils.helpers import format_car_number

router = Router(name="admin_drivers")

# ─── Haydovchilar menyusi ─────────────────────────────
@router.callback_query(F.data == "driver_manage")
async def open_driver_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    admin = await get_user_by_id(cb.from_user.id)
    role = admin.role or "admin"
    await cb.message.edit_text(
        "<b>🚖 Haydovchilar bo‘limi</b>\n\nKerakli amalni tanlang:",
        reply_markup=drivers_menu_buttons(role),
        parse_mode=ParseMode.HTML
    )
    await cb.answer()

# ─── Haydovchi qo‘shish ───────────────────────────────
@router.callback_query(F.data == "add_driver")
async def add_driver_prompt(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.adding_driver_id)
    await cb.message.answer("🆔 Haydovchi Telegram ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.adding_driver_id)
async def input_driver_id(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Faqat raqamli ID ni matn sifatida yuboring")
    user_id = int(msg.text)
    if user_id > 9223372036854775807:
        return await msg.answer("❌ Juda katta ID")
    user = await get_user_by_id(user_id)
    if not user:
        return await msg.answer("❌ Bunday foydalanuvchi topilmadi")
    async with async_session() as session:
        if await session.get(Driver, user_id):
            return await msg.answer("⚠️ Bu foydalanuvchi allaqachon haydovchi")
    await state.update_data(driver_id=user.id)
    await state.set_state(AdminManageState.adding_driver_phone)
    await msg.answer("📞 Haydovchi telefon raqamini kiriting:", reply_markup=cancel_reply_kb())

@router.message(AdminManageState.adding_driver_phone)
async def input_driver_phone(msg: Message, state: FSMContext):
    phone = normalize_phone(msg.text)
    if not phone:
        return await msg.answer("<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
            "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>")
    await state.update_data(phone=phone)
    await state.set_state(AdminManageState.adding_driver_car_model)
    await msg.answer("🚘 Haydovchi avtomobil rusumini kiriting:", reply_markup=cancel_reply_kb())

@router.message(AdminManageState.adding_driver_car_model)
async def input_car_model(msg: Message, state: FSMContext):
    car_model = msg.text.strip()
    if not car_model:
        return await msg.answer("⚠️ Iltimos, avtomobil rusumini kiriting")

    await state.update_data(car_model=car_model)
    await state.set_state(AdminManageState.adding_driver_car_number)
    await msg.answer("🔢 Avtomobilning davlat raqamini kiriting:", reply_markup=cancel_reply_kb())

@router.message(AdminManageState.adding_driver_car_number)
async def input_car_number(msg: Message, state: FSMContext):
    raw_number = msg.text.strip()
    formatted = format_car_number(raw_number)

    if not formatted:
        return await msg.answer(
            "<b>⚠️ Noto‘g‘ri format</b>\n\n<b>Namuna:</b> `01 A 123 BC` yoki `01 123 ABC`\n\n"
            "<i>Faqat O‘zbekiston raqamlariga ruxsat beriladi</i>",
            parse_mode="HTML"
        )

    await state.update_data(car_number=formatted)
    await state.set_state(AdminManageState.adding_driver_groups)
    await msg.answer("👥 Guruh ID(lar)ni kiriting (kamida bitta, vergul bilan):", reply_markup=cancel_reply_kb())

@router.message(AdminManageState.adding_driver_groups)
async def input_driver_groups(msg: Message, state: FSMContext):
    try:
        group_ids = [int(gid.strip()) for gid in msg.text.strip().split(",") if gid.strip()]
        if not group_ids:
            raise ValueError
    except:
        return await msg.answer("⚠️ Guruh ID(lar) noto‘g‘ri\n\nQuyidagicha bo'lishi zarur: -100111,-100222")

    allowed_ids = set(GROUPS.values())
    for gid in group_ids:
        if gid not in allowed_ids:
            return await msg.answer(f"🚫 {gid} — bu guruh ID bazada mavjud emas!")

    await state.update_data(group_chat_ids=group_ids)
    data = await state.get_data()
    user = await get_user_by_id(data["driver_id"])

    text = (
            f"<b>🚖 Haydovchi maʼlumotlari:</b>\n\n"
            f"👤 <b>Ismi:</b> {escape_html(user.user_fullname)}\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"🔗 <b>Username:</b> @{user.username or '—'}\n"
            f"📞 <b>Telefon:</b> {data['phone']}\n"
            f"🚘 <b>Avtomobil rusumi:</b> {escape_html(data['car_model'])}\n"
            f"🔢 <b>Davlat raqami:</b> <code>{data['car_number']}</code>\n"
            f"👥 <b>Guruhlar:</b>\n" +
            "\n".join([f"• <code>{gid}</code>" for gid in group_ids]) +
            "\n\n⚠️ <b>Ushbu foydalanuvchini qo‘shishni tasdiqlaysizmi?</b>"
    )

    await state.set_state(AdminManageState.confirming_driver_add)
    await msg.answer(text, parse_mode="HTML", reply_markup=confirm_driver_add_buttons())

@router.callback_query(AdminManageState.confirming_driver_add, F.data.in_([
    "confirm_driver_add", "retry_driver_add", "cancel_driver_add"]))
async def finish_driver_add(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if cb.data == "cancel_driver_add":
        await state.clear()
        return await cb.message.edit_text("❌ Qo‘shish bekor qilindi", reply_markup=kb_main())

    if cb.data == "retry_driver_add":
        await state.set_state(AdminManageState.adding_driver_id)
        return await cb.message.edit_text("🆔 Haydovchi ID’sini qayta kiriting:")

    user = await get_user_by_id(data["driver_id"])

    async with async_session() as session:
        if await session.get(Driver, user.id):
            await state.clear()
            return await cb.message.edit_text("⚠️ Haydovchi allaqachon mavjud")

        # Bot rejimini tekshiramiz
        setting = await session.get(Setting, "bot_mode")
        is_paid_mode = setting and setting.value == "paid"

        now = now_tashkent()
        paid_until = now + timedelta(days=1) if is_paid_mode else None

        # Haydovchini saqlaymiz
        driver = Driver(
            id=user.id,
            fullname=user.user_fullname,
            username=user.username,
            phone_number=data["phone"],
            group_chat_ids=data["group_chat_ids"],
            car_model=data["car_model"],
            car_number=data["car_number"],
            is_paid=False,
            paid_until=paid_until,
            added_by=cb.from_user.id
        )
        session.add(driver)
        await session.commit()

    # Agar pullik rejim bo‘lsa — haydovchiga xabar yuboriladi
    amount = 50000
    if is_paid_mode:
        try:
            msg_text = (
                f"Hurmatli <b>{user.user_fullname}</b>!\n\n"
                "Siz <b>Karvon Taxi</b> tizimiga haydovchi sifatida muvaffaqiyatli qo‘shildingiz!\n"
                "Botning barcha xizmatlaridan foydalanish uchun to‘lov qilishingiz lozim\n\n"
                f"💰 To‘lov miqdori: <b>{amount:,} (ellik ming) so‘m</b>\n"
                f"⏳ To‘lov qilish muddati: <b>{paid_until.strftime('%d.%m.%Y | %H:%M')} gacha</b>\n\n"
                "<b>⚠️ 24 soat ichida to‘lov qilmasangiz botdan foydalanish cheklanadi</b>"
            )
            kb = InlineKeyboardBuilder()
            kb.button(text="To'lov qilish (Click)", callback_data="tolash_click")
            kb.adjust(1)

            await bot.send_message(driver.id, msg_text, reply_markup=kb.as_markup())

        except Exception as e:
            print(f"[Xato] Haydovchiga xabar yuborilmadi: {e}")

    await cb.message.edit_text("✅ Haydovchi muvaffaqiyatli qo‘shildi!", reply_markup=kb_main())
    await state.clear()

# ─── Guruh ID qo‘shish ───────────────────────────────
@router.callback_query(F.data == "add_group_id")
async def prompt_add_group_id(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.add_group_ids)
    await cb.message.answer(
        "➕ Haydovchi ID ni kiriting:",
        reply_markup=cancel_reply_kb()
    )
    await cb.answer()

@router.message(AdminManageState.add_group_ids)
async def add_group_ids_step1(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.strip().isdigit():
        return await msg.answer("⚠️ Faqat haydovchi ID raqamini kiriting")
    driver_id = int(msg.text.strip())
    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi")
        current_groups = driver.group_chat_ids or []
    text = (
        f"<b>👤 Haydovchi:</b> {escape_html(driver.fullname)}\n"
        f"<b>🆔:</b> <code>{driver.id}</code>\n"
        f"<b>👥 Joriy guruhlar:</b>\n" +
        ("\n".join([f"• <code>{gid}</code>" for gid in current_groups]) if current_groups else "❌ Hali guruh biriktirilmagan.")
    )
    await state.update_data(driver_id=driver.id)
    await state.set_state(AdminManageState.confirming_group_add_input)
    await msg.answer(
        text + "\n\n➕ Yangi guruh ID(lar)ni kiriting (vergul bilan):",
        parse_mode="HTML",
        reply_markup=cancel_reply_kb()
    )

@router.message(AdminManageState.confirming_group_add_input)
async def confirm_adding_groups(msg: Message, state: FSMContext):
    try:
        new_ids = [int(gid.strip()) for gid in msg.text.strip().split(",") if gid.strip()]
        if not new_ids:
            raise ValueError
    except:
        return await msg.answer("⚠️ Format noto‘g‘ri\n\nMasalan: -100111,-100222")

    allowed_ids = set(GROUPS.values())
    for gid in new_ids:
        if gid not in allowed_ids:
            return await msg.answer(f"🚫 {gid} — bu guruh ID'si bizda mavjud emas!")

    data = await state.get_data()
    driver_id = data.get("driver_id")

    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi")

        current_ids = set(driver.group_chat_ids or [])
        new_unique_ids = [gid for gid in new_ids if gid not in current_ids]

        if not new_unique_ids:
            return await msg.answer("⚠️ Barcha kiritilgan guruh ID lar allaqachon biriktirilgan")

        driver.group_chat_ids = list(current_ids.union(new_unique_ids))
        await session.commit()

    await state.clear()
    await msg.answer("✅ Yangi guruh ID(lar) qo‘shildi", reply_markup=kb_main())

# ─── Haydovchini o‘chirish ───────────────────────────
@router.callback_query(F.data == "remove_driver")
async def prompt_driver_id_removal(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.removing_driver_id)
    await cb.message.answer("🗑 O‘chiriladigan haydovchi ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.removing_driver_id)
async def confirm_driver_removal(msg: Message, state: FSMContext):
    try:
        driver_id = int(msg.text.strip())
    except:
        return await msg.answer("⚠️ Noto‘g‘ri ID")

    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi")

    await state.update_data(driver_id=driver.id, fullname=driver.fullname)

    # Guruh ID larni ko‘rsatish
    group_list = driver.group_chat_ids or []
    groups_text = "\n".join([f"• <code>{gid}</code>" for gid in group_list]) if group_list else "❌ Yo‘q"

    text = (
        f"<b>Haydovchini o‘chirish:</b>\n\n"
        f"<b>👤 Ismi:</b> {escape_html(driver.fullname)}\n"
        f"<b>🆔:</b> <code>{driver.id}</code>\n"
        f"<b>🔗 Username:</b> @{driver.username or '—'}\n"
        f"<b>📞 Telefon:</b> <code>{driver.phone_number or '❌ Yo‘q'}</code>\n"
        f"<b>👥 Guruh ID(lar)i:</b>\n{groups_text}\n\n"
        f"<b>⚠️ Ushbu haydovchini rostdan ham o‘chirmoqchimisiz?</b>"
    )

    await state.set_state(AdminManageState.confirming_driver_rm)
    await msg.answer(text, parse_mode="HTML", reply_markup=confirm_remove_buttons())

@router.callback_query(AdminManageState.confirming_driver_rm, F.data.in_([
    "confirm_rm", "retry_rm", "cancel_rm"]))
async def finish_driver_removal(cb: CallbackQuery, state: FSMContext):
    if cb.data == "cancel_rm":
        await state.clear()
        await cb.message.edit_text("❌ O‘chirish bekor qilindi")  # Inline bo‘lgani uchun markup olib tashlandi
        return await cb.answer()

    if cb.data == "retry_rm":
        await state.set_state(AdminManageState.removing_driver_id)
        await cb.message.delete()
        await cb.message.answer("🔁 Haydovchi ID’sini qayta kiriting:", reply_markup=cancel_reply_kb())
        return await cb.answer()

    # confirm_rm holati:
    data = await state.get_data()
    async with async_session() as session:
        driver = await session.get(Driver, data["driver_id"])
        if driver:
            await session.delete(driver)
            await session.commit()

    await state.clear()
    await cb.message.edit_text("✅ Haydovchi o‘chirildi", reply_markup=kb_main())
    await cb.answer()

# ─── Guruh ID o‘chirish ──────────────────────────────
@router.callback_query(F.data == "remove_group_id")
async def prompt_remove_group_id(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.remove_group_ids)
    await cb.message.answer("🆔 Haydovchi Telegram ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.remove_group_ids)
async def remove_group_ids_step1(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.strip().isdigit():
        return await msg.answer("⚠️ Faqat haydovchi ID raqamini kiriting")
    driver_id = int(msg.text.strip())
    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi")
        current_groups = driver.group_chat_ids or []
    text = (
        f"<b>👤 Haydovchi:</b> {escape_html(driver.fullname)}\n"
        f"<b>🆔:</b> <code>{driver.id}</code>\n"
        f"<b>👥 Joriy guruhlar:</b>\n" +
        ("\n".join([f"• <code>{gid}</code>" for gid in current_groups]) if current_groups else "❌ Guruhlar yo‘q.")
    )
    await state.update_data(driver_id=driver.id)
    await state.set_state(AdminManageState.confirming_group_remove_input)
    await msg.answer(
        text + "\n\n➖ O‘chiriladigan guruh ID(lar)ni kiriting (vergul bilan):",
        parse_mode="HTML",
        reply_markup=cancel_reply_kb()
    )

@router.message(AdminManageState.confirming_group_remove_input)
async def confirm_group_removal(msg: Message, state: FSMContext):
    try:
        remove_ids = [int(gid.strip()) for gid in msg.text.strip().split(",") if gid.strip()]
    except:
        return await msg.answer("⚠️ Format noto‘g‘ri\n\nMasalan: -100111,-100222")

    data = await state.get_data()
    driver_id = data.get("driver_id")

    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi")

        current_ids = driver.group_chat_ids or []
        updated_ids = [gid for gid in current_ids if gid not in remove_ids]

        if len(updated_ids) == 0:
            return await msg.answer("❌ Kamida bitta guruh ID bo'lishi kerak!")

        driver.group_chat_ids = updated_ids
        await session.commit()

    await state.clear()
    await msg.answer("✅ Guruh ID(lar) o‘chirildi", reply_markup=kb_main())

# ─── Telefon raqamni tahrirlash ──────────────────────
@router.callback_query(F.data == "edit_driver_phone2")
async def ask_driver_id_for_edit(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.editing_driver_id)
    await cb.message.answer("🆔 Haydovchi Telegram ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.editing_driver_id)
async def show_current_phone_and_ask_new(msg: Message, state: FSMContext):
    try:
        driver_id = int(msg.text.strip())
    except:
        return await msg.answer("⚠️ Noto‘g‘ri ID")

    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi")

    await state.update_data(driver_id=driver_id, fullname=driver.fullname)

    current_phone = driver.phone_number or "—"
    await state.set_state(AdminManageState.editing_driver_phone)
    await msg.answer(
        f"<b>👤 Haydovchi:</b> {escape_html(driver.fullname)}\n"
        f"<b>🆔:</b> <code>{driver.id}</code>\n"
        f"<b>📞 Joriy telefon raqami:</b> {current_phone}\n\n"
        f"📞 Yangi telefon raqamni kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_reply_kb()
    )

@router.message(AdminManageState.editing_driver_phone)
async def confirm_new_phone(msg: Message, state: FSMContext):
    phone = normalize_phone(msg.text)
    if not phone:
        return await msg.answer("⚠️ Telefon raqam noto‘g‘ri\n\nMasalan: +998901234567")

    data = await state.get_data()
    driver_id = data.get("driver_id")

    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi")
        current_phone = driver.phone_number

    if phone == current_phone:
        return await msg.answer("⚠️ Yangi telefon raqam joriy raqam bilan bir xil\n\nIltimos, boshqacha raqam kiriting.")

    await state.update_data(new_phone=phone)

    text = (
        f"<b>👤 Haydovchi:</b> {escape_html(driver.fullname)}\n"
        f"<b>🆔:</b> <code>{driver.id}</code>\n"
        f"<b>📞 Yangi telefon:</b> {phone}\n\n"
        f"<b>⚠️ Tasdiqlaysizmi?</b>"
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=confirm_driver_edit_buttons())
    await state.set_state(AdminManageState.confirming_driver_phone_edit)

@router.callback_query(AdminManageState.confirming_driver_phone_edit, F.data.in_([
    "confirm_driver_edit", "cancel_driver_edit"]))
async def finish_editing_driver_phone(cb: CallbackQuery, state: FSMContext):
    if cb.data == "cancel_driver_edit":
        await state.clear()
        return await cb.message.edit_text("❌ Bekor qilindi.", reply_markup=kb_main())

    data = await state.get_data()
    async with async_session() as session:
        driver = await session.get(Driver, data["driver_id"])
        if not driver:
            return await cb.message.edit_text("❌ Topilmadi.")
        driver.phone_number = data["new_phone"]
        await session.commit()

    await state.clear()
    await cb.message.edit_text("✅ Telefon raqami yangilandi!", reply_markup=kb_main())
    await cb.answer()

@router.callback_query(F.data == "edit_car_model")
async def ask_driver_id_for_car_model(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✏️ Rusumini o‘zgartirmoqchi bo‘lgan haydovchi ID raqamini kiriting:")
    await state.set_state(AdminManageState.finding_driver_id_for_model)

@router.message(AdminManageState.finding_driver_id_for_model)
async def ask_new_car_model(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer(
            "⚠️ Iltimos, ID raqamini faqat matn ko‘rinishida kiriting\n\nRasm yoki ovozli xabar yubormang")
        return

    try:
        driver_id = int(msg.text.strip())
    except ValueError:
        await msg.answer("❌ Noto‘g‘ri ID kiritildi\n\nFaqat raqam kiriting")
        return

    async with async_session() as session:
        result = await session.execute(select(Driver).where(Driver.id == driver_id))
        driver = result.scalar_one_or_none()

        if not driver:
            await msg.answer("❌ Bunday ID raqamli haydovchi topilmadi")
            return

        await state.update_data(
            driver_id=driver.id,
            driver_fullname=driver.fullname,
            current_model=driver.car_model,
            current_number=driver.car_number
        )
        await msg.answer(
            f"👤 <b>Haydovchi:</b> {driver.fullname}\n"
            f"🚘 <b>Joriy rusum:</b> {driver.car_model or 'Kiritilmagan'}\n"
            f"🔢 <b>Joriy davlat raqami:</b> {driver.car_number or 'Kiritilmagan'}\n\n"
            f"✏️ Yangi avtomobil rusumini kiriting:",
            parse_mode="HTML"
        )
        await state.set_state(AdminManageState.waiting_for_new_car_model)

@router.message(AdminManageState.waiting_for_new_car_model)
async def confirm_car_model(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer(
            "⚠️ Iltimos, avtomobil rusumini matn ko‘rinishida kiriting\n\nRasm yoki ovozli xabar yubormang")
        return

    new_model = msg.text.strip()
    await state.update_data(new_model=new_model)
    data = await state.get_data()

    driver_fullname = data.get("driver_fullname", "Noma'lum")
    current_car_number = data.get("current_number", "Kiritilmagan")
    current_model = data.get("current_model", "Kiritilmagan")

    await msg.answer(
        f"<b>🔄 Avtomobil rusumini yangilash</b>\n\n"
        f"<b>👤 Haydovchi:</b> {driver_fullname}\n"
        f"<b>🔢 Davlat raqami:</b> {current_car_number}\n\n"
        f"<b>🚘 Joriy rusum:</b> {current_model}\n"
        f"<b>➡️ Yangi rusum:</b> {new_model}\n\n"
        f"<b>⚠️ Tasdiqlaysizmi?</b>",
        reply_markup=confirm_car_model_buttons(),
        parse_mode="HTML"
    )
    await state.set_state(AdminManageState.confirming_new_car_model)

@router.callback_query(F.data == "confirm_car_model")
async def update_car_model(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        await session.execute(
            update(Driver)
            .where(Driver.id == data["driver_id"])
            .values(car_model=data["new_model"])
        )
        await session.commit()
    await cb.message.edit_text("✅ Avtomobil rusumi muvaffaqiyatli yangilandi", reply_markup=kb_main())
    await state.clear()

@router.callback_query(F.data == "cancel_car_model")
async def cancel_car_model(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("❌ Rusum yangilash bekor qilindi", reply_markup=kb_main())
    await state.clear()

@router.callback_query(F.data == "edit_car_number")
async def ask_driver_id_for_car_number(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✏️ Davlat raqamini o‘zgartirmoqchi bo‘lgan haydovchi ID raqamini kiriting:")
    await state.set_state(AdminManageState.finding_driver_id_for_number)

@router.message(AdminManageState.finding_driver_id_for_number)
async def ask_new_car_number(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("⚠️ Iltimos, ID raqamini matn shaklida kiriting\n\nRasm yoki ovozli xabar yubormang")
        return

    try:
        driver_id = int(msg.text.strip())
    except ValueError:
        await msg.answer("❌ Noto‘g‘ri ID kiritildi\n\nFaqat raqam kiriting")
        return

    async with async_session() as session:
        result = await session.execute(select(Driver).where(Driver.id == driver_id))
        driver = result.scalar_one_or_none()

        if not driver:
            await msg.answer("❌ Bunday ID raqamli haydovchi topilmadi")
            return

        await state.update_data(driver_id=driver.id, fullname=driver.fullname,
                                current_model=driver.car_model or "Kiritilmagan",
                                current_number=driver.car_number or "Kiritilmagan")

        await msg.answer(
            f"👤 <b>Haydovchi:</b> {driver.fullname}\n"
            f"🚘 <b>Joriy rusum:</b> {driver.car_model or 'Kiritilmagan'}\n"
            f"🔢 <b>Joriy davlat raqami:</b> {driver.car_number or 'Kiritilmagan'}\n\n"
            f"✏️ Yangi davlat raqamini kiriting:",
            parse_mode="HTML"
        )
        await state.set_state(AdminManageState.waiting_for_new_car_number)

@router.message(AdminManageState.waiting_for_new_car_number)
async def confirm_car_number(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer(
            "⚠️ Iltimos, davlat raqamini faqat matn ko‘rinishida kiriting\n\nRasm yoki ovozli xabar yubormang")
        return

    formatted = format_car_number(msg.text)
    if not formatted:
        await msg.answer(
            "<b>⚠️ Noto‘g‘ri format</b>\n\n<b>Namuna:</b> `01 A 123 AA` yoki `01 123 ABC`\n\n"
            "<i>Faqat O‘zbekiston raqamlariga ruxsat beriladi</i>",
            parse_mode="HTML"
        )
        return

    await state.update_data(new_number=formatted)
    data = await state.get_data()
    driver_id = data.get("driver_id")
    if not driver_id:
        await msg.answer("❌ Haydovchi ID topilmadi.")
        return

    async with async_session() as session:
        result = await session.execute(select(Driver).where(Driver.id == driver_id))
        driver = result.scalar_one_or_none()

    if not driver:
        await msg.answer("❌ Haydovchi topilmadi.")
        return

    await msg.answer(
        f"<b>🔄 Avtomobil raqamini yangilash</b>\n\n"
        f"<b>👤 Haydovchi:</b> {driver.fullname}\n"
        f"<b>🚘 Joriy rusum:</b> {driver.car_model or 'Kiritilmagan'}\n\n"
        f"<b>🔢 Joriy raqam:</b> {driver.car_number or 'Kiritilmagan'}\n"
        f"<b>➡️ Yangi raqam:</b> {formatted}\n\n"
        f"<b>⚠️ Tasdiqlaysizmi?</b>",
        reply_markup=confirm_car_number_buttons(),
        parse_mode="HTML"
    )

    await state.set_state(AdminManageState.confirming_new_car_number)

@router.callback_query(F.data == "confirm_car_number")
async def update_car_number(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        await session.execute(
            update(Driver)
            .where(Driver.id == data["driver_id"])
            .values(car_number=data["new_number"])
        )
        await session.commit()
    await cb.message.edit_text("✅ Davlat raqami muvaffaqiyatli yangilandi", reply_markup=kb_main())
    await state.clear()

@router.callback_query(F.data == "cancel_car_number")
async def cancel_car_number(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("❌ Davlat raqamini yangilash bekor qilindi", reply_markup=kb_main())
    await state.clear()

@router.callback_query(F.data == "find_driver")
async def prompt_driver_search(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.finding_driver_id)
    await cb.message.answer("🔍 Haydovchi ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.finding_driver_id)
async def process_driver_search(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.strip().isdigit():
        return await msg.answer("⚠️ Faqat raqamli ID ni yuboring.")

    driver_id = int(msg.text.strip())
    async with async_session() as session:
        driver = await session.get(Driver, driver_id)
        if not driver:
            return await msg.answer("❌ Haydovchi topilmadi.")

        # Pullik rejimda ekanini tekshirish
        setting = await session.get(Setting, "bot_mode")
        is_paid_mode = setting and setting.value == "paid"

    group_list = driver.group_chat_ids or []
    groups_text = "\n".join([f"• <code>{gid}</code>" for gid in group_list]) if group_list else "❌ Yo‘q"

    text = (
        f"<b>🚖 Haydovchi ma’lumotlari:</b>\n\n"
        f"👤 <b>Ismi:</b> {escape_html(driver.fullname)}\n"
        f"🆔 <b>ID:</b> {driver.id}\n"
        f"🔗 <b>Username:</b> @{driver.username or '—'}\n"
        f"📞 <b>Telefon raqami:</b> {driver.phone_number or '—'}\n"
        f"🚘 <b>Avtomobil rusumi:</b> {driver.car_model}\n"
        f"🔢 <b>Davlat raqami:</b> <code>{driver.car_number}</code>\n"
        f"👥 <b>Joriy guruhlar:</b>\n{groups_text}\n"
        f"🧑‍💼 <b>Qo‘shgan admin:</b> <code>{driver.added_by}</code>\n"
        f"📅 <b>Qo‘shilgan sana:</b> {driver.joined_at.strftime('%d.%m.%Y | %H:%M') if driver.joined_at else '—'}"
    )

    if is_paid_mode:
        tolov_holati = "✅ To‘langan" if driver.is_paid else "❌ To‘lanmagan"
        obuna_muddati = (
            driver.paid_until.strftime("%d.%m.%Y | %H:%M") if driver.paid_until else "—"
        )

        text += (
            f"\n\n💳 <b>To‘lov holati:</b> {tolov_holati}\n"
            f"⏳ <b>Obuna muddati:</b> {obuna_muddati}"
        )

    await state.clear()
    await msg.answer(text, parse_mode="HTML", reply_markup=kb_back2())

@router.callback_query(F.data == "driver_stats")
async def show_driver_stats(cb: CallbackQuery):
    async with async_session() as session:
        now = now_tashkent()

        # Soat oraliqlari
        one_day_ago = now - timedelta(days=1)
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        one_year_ago = now - timedelta(days=365)

        # Umumiy va vaqtga qarab haydovchilar
        total_drivers = await session.scalar(select(func.count()).select_from(Driver))
        one_day = await session.scalar(select(func.count()).select_from(Driver).where(Driver.joined_at >= one_day_ago))
        seven_days = await session.scalar(select(func.count()).select_from(Driver).where(Driver.joined_at >= seven_days_ago))
        thirty_days = await session.scalar(select(func.count()).select_from(Driver).where(Driver.joined_at >= thirty_days_ago))
        one_year = await session.scalar(select(func.count()).select_from(Driver).where(Driver.joined_at >= one_year_ago))

        # Bot rejimi (pullik yoki bepul)
        mode = await session.scalar(
            select(Setting.value).where(Setting.key == "bot_mode")
        )

        is_paid_mode = (mode == "paid")  # yoki "pullik" deb saqlangan bo‘lsa, shunga moslashtiring

        # Matnni tayyorlash
        text = (
            "<b>📊 Haydovchilar statistikasi</b>\n\n"
            "<b>🆕 Yangi qo‘shilganlar:</b>\n"
            f"• Bir kunda: <b>{one_day} ta</b>\n"
            f"• Bir haftada: <b>{seven_days} ta</b>\n"
            f"• Bir oyda: <b>{thirty_days} ta</b>\n"
            f"• Bir yilda: <b>{one_year} ta</b>\n\n"
        )
        # To‘lov holatini faqat pullik rejimda chiqarish
        if is_paid_mode:
            paid_drivers = await session.scalar(select(func.count()).select_from(Driver).where(Driver.is_paid == True))
            unpaid_drivers = total_drivers - paid_drivers

            text += (
                "<b>💰 To‘lov holati:</b>\n"
                f"• To‘lov qilganlar: <b>{paid_drivers} ta</b>\n"
                f"• To‘lov qilmaganlar: <b>{unpaid_drivers} ta</b>\n\n"
            )
        text += f"👥 Umumiy haydovchilar: <b>{total_drivers} ta</b>"

    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb_back2())
    await cb.answer()

def format_announcement_info(announcement: Announcement) -> str:
    """Faol e'lon tafsilotlarini matnga aylantiradi"""
    return (
        f"<b>🚖 Haydovchi ID:</b> {announcement.driver_id}\n"
        f"<b>📍 Yo'nalish:</b> {announcement.from_vil} ➝ {announcement.to_vil}\n"
        f"<b>📝 Izoh:</b> {announcement.text}\n"
        f"<b>🕒 Vaqt:</b> {announcement.created_at:%d-%m-%Y | %H:%M}\n\n"
        f"<b>❓ Ushbu e'lonni to'xtatmoqchimisiz?</b>"
    )

# 1️⃣ Admin boshlaydi (matn orqali)
@router.message(F.text == "❌ E'lonni to'xtatish")
async def ask_driver_id(msg: Message, state: FSMContext):
    await msg.answer("🔎 Haydovchi ID sini kiriting:")
    await state.set_state(AdminAnnouncementStates.waiting_driver_id)

# 1️⃣ Admin boshlaydi (inline tugma orqali)
@router.callback_query(F.data == "stop_driver_announce")
async def ask_driver_id_from_admin(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("🔎 Haydovchi ID sini kiriting:")
    await state.set_state(AdminAnnouncementStates.waiting_driver_id)
    await cb.answer()

# 2️⃣ Admin ID kiritganda
@router.message(AdminAnnouncementStates.waiting_driver_id)
async def show_driver_announcement(msg: Message, state: FSMContext):
    try:
        driver_id = int(msg.text)
    except ValueError:
        await msg.answer("❌ Noto‘g‘ri ID. Faqat raqam kiriting")
        return

    # DB session ochish
    async with async_session() as session:
        driver = await get_driver_by_id(session, driver_id)

    if not driver:
        await msg.answer(f"❌ Haydovchi ID {driver_id} topilmadi")
        await state.clear()
        return

    # Keyin faol e'lonini tekshiramiz
    announcement = await get_active_announcement_by_driver(driver_id)
    if not announcement:
        await msg.answer(f"ℹ️ Haydovchi {driver.fullname} (ID {driver_id}) uchun faol e'lon mavjud emas")
        await state.clear()
        return

    # Faol e'lonni ko'rsatish
    await msg.answer(
        format_announcement_info(announcement),
        reply_markup=confirm_stop_announce_buttons(announcement.id)
    )
    await state.set_state(AdminAnnouncementStates.confirm_stop)

# 3️⃣ Tasdiqlash yoki bekor qilish
@router.callback_query(F.data.startswith("admin_confirm_stop"))
async def confirm_stop(cb: CallbackQuery, state: FSMContext):
    await cb.answer("✅ To'xtatildi")
    announcement_id = int(cb.data.split(":")[1])

    await deactivate_announcement(announcement_id)
    await cb.message.edit_text("✅ E'lon muvaffaqiyatli to'xtatildi", reply_markup=kb_main())
    await state.clear()

@router.callback_query(F.data == "admin_cancel_stop")
async def cancel_stop(cb: CallbackQuery, state: FSMContext):
    await cb.answer("❌ Bekor qilindi")
    await cb.message.edit_text("❌ Amal bekor qilindi", reply_markup=kb_main())
    await state.clear()