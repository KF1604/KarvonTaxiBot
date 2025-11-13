from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from app.database.session import async_session
from app.keyboards import to_main_menu_inline
from app.states.admin_states import AdminManageState
from app.keyboards.admin_reply import cancel_reply_kb
from app.keyboards.admin_inline import users_menu_buttons, confirm_block, confirm_unblock, confirm_deleteuser, \
    kb_back3
from sqlalchemy import select
from app.database.models import User, Driver

router = Router(name="admin_users")

@router.callback_query(F.data == "manage_users")
async def show_users_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        admin = await session.get(User, cb.from_user.id)
        role = admin.role

    await cb.message.edit_text(
        "<b>👤 Foydalanuvchilar bo‘limi</b>\n\nKerakli amalni tanlang:",
        parse_mode=ParseMode.HTML,
        reply_markup=users_menu_buttons(role=role)
    )
    await cb.answer()

# 🔍 Foydalanuvchini topish
@router.callback_query(F.data == "find_user")
async def prompt_find_user(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.finding_user)
    await cb.message.answer("🔍 Qidirilayotgan foydalanuvchi ID’sini yuboring:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.finding_user)
async def find_user(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Faqat raqamli ID yuboring")
    user_id = int(msg.text)

    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return await msg.answer("❌ Foydalanuvchi topilmadi")

        # Haydovchimi yo'qmi aniqlaymiz
        driver_result = await session.execute(
            select(Driver).where(Driver.id == user.id)
        )
        is_driver = driver_result.scalar_one_or_none() is not None

    await state.clear()

    # Roli + haydovchilik holati
    role_display = user.role
    if user.role == "user" and is_driver:
        role_display += ", haydovchi"
    elif user.role != "user" and is_driver:
        role_display += " (haydovchi)"

    # To‘liq ma'lumot
    text = (
        f"<b>👤 Foydalanuvchi:</b> {user.user_fullname}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>🔗 Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"<b>📞 Telefon:</b> <code>{user.phone_number if user.phone_number else 'yo‘q'}</code>\n"
        f"<b>🎭 Roli:</b> {role_display}\n"
        f"<b>📌 Holati:</b> {'🚫Bloklangan' if user.is_blocked else '✅Faol'}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {user.joined_at.strftime('%d.%m.%Y | %H:%M')}\n"
    )

    await msg.answer(text, parse_mode="HTML", reply_markup=kb_back3())

# 🚫 Bloklash (tasdiq bilan)
@router.callback_query(F.data == "block_user")
async def prompt_block_user(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.blocking_user)
    await cb.message.answer("🚫 Bloklash uchun foydalanuvchi ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.blocking_user)
async def block_user_step(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Faqat raqamli ID yuboring.")
    user_id = int(msg.text)

    async with async_session() as session:
        admin = await session.get(User, msg.from_user.id)
        user = await session.get(User, user_id)

        if not user:
            return await msg.answer("❌ Foydalanuvchi topilmadi")
        if user.role == "owner":
            return await msg.answer("❌ Ega bloklanmaydi")
        if user.role == "super_admin" and admin.role != "owner":
            return await msg.answer("❌ Super adminni faqat Ega bloklashi mumkin")
        if user.is_blocked:
            return await msg.answer("ℹ️ Ushbu foydalanuvchi allaqachon bloklangan")

        # Haydovchiligi tekshiriladi
        driver_check = await session.execute(select(Driver).where(Driver.id == user.id))
        is_driver = driver_check.scalar_one_or_none() is not None

    await state.update_data(block_id=user_id)

    role_display = f"{user.role} (haydovchi)" if is_driver else user.role

    text = (
        f"<b>🚫 Foydalanuvchini bloklash</b>\n\n"
        f"<b>👤 Foydalanuvchi:</b> {user.user_fullname}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>🔗 Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"<b>📞 Telefon:</b> <code>{user.phone_number if user.phone_number else 'yo‘q'}</code>\n"
        f"<b>🎭 Roli:</b> {role_display}\n"
        f"<b>📌 Holati:</b> {'🚫Bloklangan' if user.is_blocked else '✅Faol'}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {user.joined_at.strftime('%d.%m.%Y | %H:%M')}\n\n"
        f"⚠️ Ushbu foydalanuvchini bloklashni tasdiqlaysizmi?"
    )

    await msg.answer(text, parse_mode="HTML", reply_markup=confirm_block())

@router.callback_query(F.data == "confirm_block")
async def confirm_block_user(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("block_id")
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user.role != "owner":
            if user.role != "user":
                user.role = "user"
            user.is_blocked = True
            await session.commit()
            await cb.message.edit_text("✅ Foydalanuvchi bloklandi", reply_markup=kb_back3())
        else:
            await cb.message.edit_text("❌ Ega bloklanmaydi")
    await state.clear()
    await cb.answer()

# ♻️ Blokdan chiqarish (tasdiq bilan)
@router.callback_query(F.data == "unblock_user")
async def prompt_unblock_user(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.unblocking_user)
    await cb.message.answer("♻️ Blokdan chiqarish uchun foydalanuvchi ID’sini kiriting:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.unblocking_user)
async def unblock_user_step(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Faqat raqamli ID yuboring")
    user_id = int(msg.text)

    async with async_session() as session:
        admin = await session.get(User, msg.from_user.id)
        user = await session.get(User, user_id)

        if not user:
            return await msg.answer("❌ Foydalanuvchi topilmadi")
        if user.role == "super_admin" and admin.role != "owner":
            return await msg.answer("❌ Super adminni faqat Ega blokdan chiqarishi mumkin")
        if not user.is_blocked:
            return await msg.answer("ℹ️ Ushbu foydalanuvchi allaqachon faol")

        driver_check = await session.execute(select(Driver).where(Driver.id == user.id))
        is_driver = driver_check.scalar_one_or_none() is not None

    await state.update_data(unblock_id=user_id)

    role_display = f"{user.role} (haydovchi)" if is_driver else user.role

    text = (
        f"<b>♻️ Foydalanuvchini blokdan chiqarish</b>\n\n"
        f"<b>👤 Foydalanuvchi:</b> {user.user_fullname}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>🔗 Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"<b>📞 Telefon:</b> <code>{user.phone_number if user.phone_number else 'yo‘q'}</code>\n"
        f"<b>🎭 Roli:</b> {role_display}\n"
        f"<b>📌 Holati:</b> {'🚫Bloklangan' if user.is_blocked else '✅Faol'}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {user.joined_at.strftime('%d.%m.%Y | %H:%M')}\n\n"
        f"❓ Blokdan chiqarilsinmi?"
    )

    await msg.answer(text, parse_mode="HTML", reply_markup=confirm_unblock())

@router.callback_query(F.data == "confirm_unblock")
async def confirm_unblock_user(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("unblock_id")
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.is_blocked = False
        await session.commit()
    await cb.message.edit_text("✅ Foydalanuvchi blokdan chiqarildi", reply_markup=kb_back3())
    await state.clear()
    await cb.answer()

# 🗑 O‘chirish (tasdiq bilan)
@router.callback_query(F.data == "delete_user")
async def prompt_delete_user(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.deleting_user)
    await cb.message.answer("🗑 O‘chirish uchun foydalanuvchi ID sini yuboring:", reply_markup=cancel_reply_kb())
    await cb.answer()

@router.message(AdminManageState.deleting_user)
async def delete_user_step(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Faqat raqamli ID yuboring")
    user_id = int(msg.text)

    async with async_session() as session:
        admin = await session.get(User, msg.from_user.id)
        user = await session.get(User, user_id)

        if not user:
            return await msg.answer("❌ Foydalanuvchi topilmadi yoki allaqachon o‘chirilgan")
        if user.role == "owner":
            return await msg.answer("❌ Egani o‘chirib bo‘lmaydi")
        if user.role == "super_admin" and admin.role != "owner":
            return await msg.answer("❌ Super adminni faqat Ega o‘chira oladi")

        driver_check = await session.execute(select(Driver).where(Driver.id == user.id))
        is_driver = driver_check.scalar_one_or_none() is not None

    await state.update_data(delete_id=user_id)

    role_display = f"{user.role} (haydovchi)" if is_driver else user.role

    text = (
        f"<b>🗑 Foydalanuvchini o‘chirish</b>\n\n"
        f"<b>👤 Foydalanuvchi:</b> {user.user_fullname}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>🔗 Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"<b>📞 Telefon:</b> <code>{user.phone_number if user.phone_number else 'yo‘q'}</code>\n"
        f"<b>🎭 Roli:</b> {role_display}\n"
        f"<b>📌 Holati:</b> {'🚫Bloklangan' if user.is_blocked else '✅Faol'}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {user.joined_at.strftime('%d.%m.%Y | %H:%M')}\n\n"
        f"⚠️ Haqiqatan ham ushbu foydalanuvchini o‘chirmoqchimisiz?"
    )

    await msg.answer(text, parse_mode="HTML", reply_markup=confirm_deleteuser())

@router.callback_query(F.data == "confirm_delete")
async def confirm_delete_user(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("delete_id")
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user.role != "owner":
            await session.delete(user)
            await session.commit()
            await cb.message.edit_text("✅ Foydalanuvchi o‘chirildi", reply_markup=kb_back3())
        else:
            await cb.message.edit_text("❌ Egani o‘chirib bo‘lmaydi")
    await state.clear()
    await cb.answer()

# ✉️ Foydalanuvchiga yozish — ID kiritish bosqichi
@router.callback_query(F.data == "message_user")
async def prompt_message_user(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageState.messaging_user)
    await cb.message.answer("✉️ Xabar yuboriladigan foydalanuvchi ID’sini kiriting:",
                            reply_markup=cancel_reply_kb())
    await cb.answer()

# 🧾 ID kiritilgandan so‘ng — foydalanuvchi haqida ma’lumot chiqarish
@router.message(AdminManageState.messaging_user)
async def ask_message_text(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        return await msg.answer("⚠️ Foydalanuvchi ID noto‘g‘ri")

    user_id = int(msg.text)

    # ❌ O'ziga xabar yuborishga ruxsat yo'q
    if user_id == msg.from_user.id:
        return await msg.answer("❌ O'zingizga xabar yoza olmaysiz")

    async with async_session() as session:
        # Admin o‘zi
        admin = await session.get(User, msg.from_user.id)
        # Foydalanuvchi
        user = await session.get(User, user_id)

        if not user:
            return await msg.answer("❌ Foydalanuvchi topilmadi")

        # 👮‍♂️ Ruxsat tekshiruvi
        if admin.role == "super_admin" and user.role in ["super_admin", "owner"]:
            return await msg.answer("❌ Siz ushbu foydalanuvchiga xabar yubora olmaysiz")
        if admin.role == "admin" and user.role in ["admin", "super_admin", "owner"]:
            return await msg.answer("❌ Siz faqat oddiy foydalanuvchilarga yozishingiz mumkin")

        # Haydovchi yoki yo‘qligini aniqlaymiz
        from app.database.models import Driver
        from sqlalchemy import select
        driver_check = await session.execute(select(Driver).where(Driver.id == user.id))
        is_driver = driver_check.scalar_one_or_none() is not None

    await state.update_data(target_user_id=user.id)

    role_display = f"{user.role} (haydovchi)" if is_driver else user.role

    text = (
        f"<b>💬 Foydalanuvchiga yozish</b>\n\n"
        f"<b>👤 Foydalanuvchi:</b> {user.user_fullname}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>🔗 Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"<b>📞 Telefon:</b> {user.phone_number if user.phone_number else 'yo‘q'}\n"
        f"<b>🎭 Roli:</b> {role_display}\n"
        f"<b>📌 Holati:</b> {'🚫Bloklangan' if user.is_blocked else '✅Faol'}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {user.joined_at.strftime('%d.%m.%Y | %H:%M')}\n\n"
        f"💬 Ushbu foydalanuvchiga xabar yubormoqchimisiz?"
    )

    buttons = [
        [InlineKeyboardButton(text="✍️ Yozish", callback_data="write_to_user")],
        [InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="manage_users")]
    ]

    await msg.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data == "write_to_user")
async def get_message_text(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await cb.message.answer("✍️ Xabar matnini yuboring:", reply_markup=cancel_reply_kb())
    await state.set_state(AdminManageState.messaging_user_text)

@router.message(AdminManageState.messaging_user_text)
async def send_message_to_user(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("target_user_id")

    if not user_id:
        return await msg.answer("⚠️ Foydalanuvchi aniqlanmadi. Qaytadan urinib ko‘ring.")

    async with async_session() as session:
        admin = await session.get(User, msg.from_user.id)

    try:
        await msg.bot.send_message(
            chat_id=user_id,
            text=(
                f"<b>📩 Sizga admindan xabar keldi</b>\n\n"
                f"<b>💬 Xabar matni:</b> {msg.text}"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"reply_to_admin_{admin.id}")]
            ])
        )
    except:
        return await msg.answer("❌ Xabar yuborib bo‘lmadi. Ehtimol, foydalanuvchi botni bloklagan",
                                reply_markup=to_main_menu_inline())

    await msg.answer("✅ Xabar yuborildi", reply_markup=to_main_menu_inline())
    await state.clear()

@router.callback_query(F.data.startswith("reply_to_admin_"))
async def prompt_reply_to_admin(cb: CallbackQuery, state: FSMContext):
    admin_id = int(cb.data.split("_")[-1])
    await state.update_data(reply_admin_id=admin_id)
    await cb.message.answer("✍️ Admin uchun javob xabarini yozing:")
    await state.set_state(AdminManageState.replying_to_admin)
    await cb.answer()

@router.message(AdminManageState.replying_to_admin)
async def send_reply_to_admin(msg: Message, state: FSMContext):
    data = await state.get_data()
    admin_id = data.get("reply_admin_id")

    if not admin_id:
        return await msg.answer("⚠️ Admin ID aniqlanmadi")

    async with async_session() as session:
        user = await session.get(User, msg.from_user.id)

        from app.database.models import Driver
        driver_check = await session.execute(select(Driver).where(Driver.id == user.id))
        is_driver = driver_check.scalar_one_or_none() is not None

    role_display = f"{user.role} (haydovchi)" if is_driver else user.role

    text = (
        f"<b>📬 Foydalanuvchidan javob:</b>\n\n"
        f"<b>👤 Foydalanuvchi:</b> {user.user_fullname}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>🔗 Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"<b>📞 Telefon:</b> {user.phone_number if user.phone_number else 'yo‘q'}\n"
        f"<b>🎭 Roli:</b> {role_display}\n"
        f"<b>📌 Holati:</b> {'🚫Bloklangan' if user.is_blocked else '✅Faol'}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {user.joined_at.strftime('%d.%m.%Y | %H:%M')}\n\n"
        f"<b>💬 Xabar matni:</b> {msg.text}"
    )

    try:
        await msg.bot.send_message(
            chat_id=admin_id,
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"admin_reply_to_user_{user.id}")]
                ]
            )
        )
    except:
        return await msg.answer("❌ Xabar yuborib bo‘lmadi, admin botni to‘xtatgan bo‘lishi mumkin")

    await msg.answer("✅ Javob xabaringiz yuborildi", reply_markup=to_main_menu_inline())
    await state.clear()

@router.callback_query(F.data.startswith("admin_reply_to_user_"))
async def prompt_admin_reply(cb: CallbackQuery, state: FSMContext):
    user_id = int(cb.data.split("_")[-1])
    await state.set_state(AdminManageState.admin_replying_user)
    await state.update_data(reply_user_id=user_id)
    await cb.message.answer("✍️ Javob matnini yozing:")
    await cb.answer()

@router.message(AdminManageState.admin_replying_user)
async def send_admin_reply_to_user(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reply_user_id")

    try:
        await msg.bot.send_message(
            chat_id=user_id,
            text=(
                f"<b>📩 Sizga admindan javob</b>\n\n"
                f"<b>💬 Xabar matni:</b> {msg.text}"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"reply_to_admin_{msg.from_user.id}")]
                ]
            )
        )
    except:
        return await msg.answer("❌ Foydalanuvchiga javob yuborilmadi. U botni to‘xtatgan bo‘lishi mumkin",
                                reply_markup=to_main_menu_inline())

    await msg.answer("✅ Javob yuborildi", reply_markup=to_main_menu_inline())
    await state.clear()

@router.callback_query(F.data == "user_blocked_alert")
async def alert_account_blocked(cb: CallbackQuery):
    await cb.answer("❌ Ushbu foydalanuvchi bloklangan yoki botni to‘xtatgan", show_alert=True)