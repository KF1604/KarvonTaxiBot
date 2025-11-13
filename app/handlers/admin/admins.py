from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime

from app.database.session import async_session
from app.database.models import User
from app.database.queries import (
    get_user_by_id, get_admin_users
)
from app.keyboards.admin_inline import (
    admin_manage_buttons, admin_role_buttons,
    confirm_admin_button, confirm_remove_button, kb_main, kb_back
)
from app.keyboards.admin_reply import cancel_reply_kb
from app.states.admin_states import AdminManageState
from app.utils.text_tools import escape_html
from app.utils.helpers import normalize_phone

router = Router(name="admin_admins")

@router.callback_query(F.data == "admin_manage")
async def manage_admins(cb: CallbackQuery):
    role = (await get_user_by_id(cb.from_user.id)).role
    await cb.message.edit_text(
        "<b>👥 Adminlar bo‘limi</b>\n\nKerakli amalni tanlang:",
        reply_markup=admin_manage_buttons(role),
        parse_mode=ParseMode.HTML
    )
    await cb.answer()

@router.callback_query(F.data == "list_admins")
async def list_admins(cb: CallbackQuery):
    viewer = await get_user_by_id(cb.from_user.id)
    admins = await get_admin_users()

    if not admins:
        await cb.message.edit_text("❌ Hozircha hech qanday admin mavjud emas", reply_markup=kb_main())
        return

    def get_visible_info(viewer: User, admin: User) -> tuple[str, str]:
        is_self = viewer.id == admin.id
        if viewer.role == "owner":
            return f"<code>{admin.id}</code>", admin.phone_number
        if viewer.role == "super_admin":
            if is_self or admin.role == "admin":
                return f"<code>{admin.id}</code>", admin.phone_number
        if viewer.role == "admin":
            if is_self:
                return f"<code>{admin.id}</code>", admin.phone_number
        return "⚫ Maxfiy", "⚫ Maxfiy"

    text = "<b>👥 Adminlar ro‘yxati:</b>\n\n"
    for admin in admins:
        is_self = viewer.id == admin.id
        note = " (siz)" if is_self else ""
        role = admin.role.capitalize().replace("_", " ") if admin.role else "Nomaʼlum"
        admin_id, phone = get_visible_info(viewer, admin)

        text += (
            f"👤 <b>Admin:</b> {escape_html(admin.user_fullname)}{note}\n"
            f"🎭 <b>Rol:</b> {role}\n"
            f"🆔 <b>ID:</b> <code>{admin_id}</code>\n"
            f"📞 <b>Telefon raqami:</b> {phone}\n"
            f"{'─' * 20}\n\n"
        )

    await cb.message.edit_text(text.strip(), parse_mode=ParseMode.HTML, reply_markup=kb_back())
    await cb.answer()

@router.callback_query(F.data == "add_admin")
async def add_admin_prompt(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.adding_user_id)
    await cb.message.answer("1️⃣ Admin Telegram ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.adding_user_id)
async def input_admin_id(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Noto‘g‘ri ID! Faqat raqamlardan iborat Telegram ID yuboring")

    user_id = int(msg.text)

    # 🔍 Baza ichidan tekshiramiz
    db_user = await get_user_by_id(user_id)

    if not db_user:
        return await msg.answer("⚠️ Bu foydalanuvchi botdan foydalanmagan, avval u /start bosishi kerak")

    # 🚫 Bloklangan bo‘lsa — admin qilib bo‘lmaydi
    if db_user.is_blocked:
        return await msg.answer("⚠️ Foydalanuvchi bloklangan, avval uni blokdan chiqaring")

    # ℹ️ Allaqachon admin
    if db_user.role in ["admin", "super_admin", "owner"]:
        return await msg.answer("ℹ️ Bu foydalanuvchi allaqachon admin")

    # ✅ Keyingi bosqich
    await state.update_data(user_id=user_id)
    await state.set_state(AdminManageState.adding_phone)
    await msg.answer("2️⃣ Admin telefon raqamini kiriting:", reply_markup=cancel_reply_kb())

@router.message(AdminManageState.adding_phone)
async def input_admin_phone(msg: Message, state: FSMContext):
    phone = normalize_phone(msg.text)
    if not phone:
        await msg.answer("<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
            "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>")
        return

    await state.update_data(phone=phone)
    await state.set_state(AdminManageState.choosing_role)

    me = await get_user_by_id(msg.from_user.id)
    await msg.answer("3️⃣ Admin rolini tanlang:", reply_markup=admin_role_buttons(me.role))

@router.callback_query(AdminManageState.choosing_role, F.data.in_(["admin", "super_admin", "cancel_add"]))
async def confirm_admin_info(cb: CallbackQuery, state: FSMContext):
    if cb.data == "cancel_add":
        await state.clear()
        await cb.message.edit_text("❌ Admin qo‘shish bekor qilindi", reply_markup=kb_main())
        return

    await state.update_data(role=cb.data)
    data = await state.get_data()
    target = await get_user_by_id(data["user_id"])

    msg = (
        f"👤 <b>Admin:</b> {escape_html(target.user_fullname)}\n"
        f"🎭 <b>Rol:</b> {data['role'].replace('_', ' ').capitalize()}\n"
        f"🆔 <b>ID:</b> <code>{data['user_id']}</code>\n"
        f"📞 <b>Telefon raqami:</b> {data['phone']}"
    )

    await state.set_state(AdminManageState.confirming_add)
    await cb.message.edit_text("4️⃣ Admin maʼlumotlarini tasdiqlang:\n\n" + msg, parse_mode="HTML", reply_markup=confirm_admin_button())
    await cb.answer()

@router.callback_query(AdminManageState.confirming_add, F.data.in_(["confirm_add", "retry_add", "cancel_add"]))
async def finish_adding_admin(cb: CallbackQuery, state: FSMContext):
    if cb.data == "cancel_add":
        await state.clear()
        await cb.message.edit_text("❌ Admin qo‘shish bekor qilindi", reply_markup=kb_main())
        return

    if cb.data == "retry_add":
        await state.set_state(AdminManageState.adding_phone)
        await cb.message.edit_text("1️⃣ Admin telefon raqamini qayta kiriting:")
        return

    data = await state.get_data()
    async with async_session() as session:
        user = await session.get(User, data["user_id"])
        user.phone_number = data["phone"]
        user.role = data["role"]
        user.joined_at = user.joined_at or datetime.utcnow()
        await session.commit()

    await cb.message.edit_text("✅ Admin ro‘yxatga qo‘shildi!", reply_markup=kb_main())
    await state.clear()

@router.callback_query(F.data == "change_admin_role")
async def prompt_admin_id_for_role_change(cb: CallbackQuery, state: FSMContext):
    current_user = await get_user_by_id(cb.from_user.id)
    if current_user.role != "owner":
        await cb.answer("❌ Sizda bunday huquq yo‘q", show_alert=True)
        return

    await state.set_state(AdminManageState.role_change_id)
    await cb.message.answer(
        "🆔 Rolini o‘zgartirmoqchi bo‘lgan adminning Telegram ID sini kiriting:",
        reply_markup=cancel_reply_kb()
    )
    await cb.answer()

@router.message(AdminManageState.role_change_id)
async def input_id_for_role_change(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        await msg.answer("⚠️ Noto‘g‘ri ID! Faqat raqamlardan iborat Telegram ID yuboring")
        return

    target_id = int(msg.text)
    db_user = await get_user_by_id(target_id)
    if not db_user:
        await msg.answer("❌ Bunday foydalanuvchi topilmadi")
        return

    if db_user.role == "owner":
        await msg.answer("🔐 Bu foydalanuvchi <b>EGA</b>. Uning rolini o‘zgartirib bo‘lmaydi", parse_mode=ParseMode.HTML)
        return

    if db_user.role not in ["admin", "super_admin"]:
        await msg.answer("ℹ️ Bu foydalanuvchi admin emas")
        return

    await state.update_data(user_id=db_user.id, old_role=db_user.role)

    me = await get_user_by_id(msg.from_user.id)
    msg_text = (
        f"👤 <b>Admin:</b> {escape_html(db_user.user_fullname)}\n"
        f"🎭 <b>Rol:</b> {db_user.role.replace('_', ' ').capitalize()}\n"
        f"🆔 <b>ID:</b> <code>{db_user.id}</code>\n"
        f"📞 <b>Telefon raqami:</b> {db_user.phone_number or '—'}\n\n"
        f"🔽 <b>Yangi rolni tanlang:</b>"
    )

    await state.set_state(AdminManageState.role_change_choose)
    await msg.answer(msg_text, reply_markup=admin_role_buttons(me.role), parse_mode=ParseMode.HTML)

@router.callback_query(AdminManageState.role_change_choose, F.data.in_(["admin", "super_admin", "cancel_add"]))
async def confirm_role_change(cb: CallbackQuery, state: FSMContext):
    if cb.data == "cancel_add":
        await state.clear()
        await cb.message.edit_text("❌ Rolni o‘zgartirish bekor qilindi.", reply_markup=kb_main())
        return

    me = await get_user_by_id(cb.from_user.id)
    if me.role != "owner":
        await cb.answer("❌ Sizda bunday huquq yo‘q", show_alert=True)
        return

    data = await state.get_data()
    user_id = data["user_id"]
    old_role = data.get("old_role", "Noma'lum")

    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            await cb.message.edit_text("❌ Foydalanuvchi topilmadi.")
            await state.clear()
            return

        user.role = cb.data
        await session.commit()

    msg_text = (
        f"✅ <b>Admin roli muvaffaqiyatli yangilandi!</b>\n\n"
        f"👤 <b>Admin:</b> {escape_html(user.user_fullname)}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"📞 <b>Telefon raqami:</b> {user.phone_number or '—'}\n"
        f"🔁 <b>{old_role.upper()}</b> ➡️ <b>{cb.data.upper()}</b>"
    )

    await cb.message.edit_text(msg_text, reply_markup=kb_main(), parse_mode=ParseMode.HTML)
    await state.clear()

@router.callback_query(F.data == "remove_admin")
async def prompt_admin_id_for_removal(cb: CallbackQuery, state: FSMContext):
    me = await get_user_by_id(cb.from_user.id)
    if me.role not in ["owner", "super_admin"]:
        await cb.answer("❌ Sizda adminni o‘chirish huquqi yo‘q.", show_alert=True)
        return

    await state.set_state(AdminManageState.removing_id)
    await cb.message.answer(
        "🗑 O‘chirmoqchi bo‘lgan adminning Telegram ID sini kiriting:",
        reply_markup=cancel_reply_kb()
    )
    await cb.answer()

@router.message(AdminManageState.removing_id)
async def confirm_admin_removal(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Noto‘g‘ri ID! Raqamli Telegram ID yuboring.")

    target_id = int(msg.text)
    remover_id = msg.from_user.id

    remover = await get_user_by_id(remover_id)
    target_user = await get_user_by_id(target_id)

    if not target_user:
        return await msg.answer("❌ Bunday foydalanuvchi topilmadi")

    # ❌ O‘zini o‘chira olmaydi
    if remover_id == target_id:
        return await msg.answer("❌ O‘zingizni o‘chira olmaysiz")

    # ❌ Ownerni hech kim o‘chira olmaydi
    if target_user.role == "owner":
        return await msg.answer("🚫 Egani (owner) o‘chirish mumkin emas")

    # 🔐 Admin emasligi tekshiruvi
    if target_user.role not in ["admin", "super_admin", "owner"]:
        return await msg.answer("ℹ️ Bu foydalanuvchi adminlar ro‘yxatida mavjud emas")

    # 🔒 Super Admin faqat oddiy adminni o‘chira oladi
    if remover.role == "super_admin" and target_user.role in ["super_admin"]:
        return await msg.answer("❌ Siz faqat oddiy adminni o‘chira olasiz")

    # ✅ Holatni saqlaymiz va tasdiqlash so‘raymiz
    await state.update_data(user_id=target_id)
    await state.set_state(AdminManageState.confirming_rm)

    await msg.answer(
        f"<b>🗑 Adminni o‘chirish</b>\n\n"
        f"<b>👤 Ismi:</b> {escape_html(target_user.user_fullname)}\n"
        f"<b>🎭 Roli:</b> {target_user.role.replace('_', ' ').capitalize()}\n"
        f"<b>🆔 ID:</b> <code>{target_user.id}</code>\n\n"
        f"<b>📞 Telefon raqami:</b> {target_user.phone_number or '—'}\n"
        f"Ushbu adminni o‘chirishni tasdiqlaysizmi?",
        parse_mode=ParseMode.HTML,
        reply_markup=confirm_remove_button()
    )

@router.callback_query(AdminManageState.confirming_rm, F.data.in_(["confirm_rm", "retry_rm", "cancel_rm"]))
async def finish_removal(cb: CallbackQuery, state: FSMContext):
    if cb.data == "cancel_rm":
        await state.clear()
        await cb.message.edit_text("❌ Admin o‘chirish bekor qilindi", reply_markup=kb_main())
        return

    if cb.data == "retry_rm":
        await state.set_state(AdminManageState.removing_id)
        await cb.message.edit_text("🔁 Qayta urining: Admin ID sini yuboring.")
        return

    data = await state.get_data()
    async with async_session() as session:
        user = await session.get(User, data["user_id"])
        user.role = "user"
        await session.commit()

    await cb.message.edit_text("✅ Admin ro‘yxatdan o‘chirildi!", reply_markup=kb_main())
    await state.clear()