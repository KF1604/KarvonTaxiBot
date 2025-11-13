from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.keyboards.admin_inline import kb_main, confirm_ad_buttons
from app.keyboards.admin_reply import cancel_reply_kb
from app.states.admin_states import AdminManageState
from app.database.session import async_session
from sqlalchemy import select
from app.database.models import User
from dispatcher import bot

router = Router(name="admin_ads")

@router.callback_query(F.data == "send_ads")
async def prompt_ads_message(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AdminManageState.forward_ads)
    await cb.message.answer(
        "📢 'Forward' qilinadigan xabarni yuboring (rasm, video, matn, tugma ham bo‘lishi mumkin):",
        reply_markup=cancel_reply_kb()
    )
    await cb.answer()

@router.message(AdminManageState.forward_ads)
async def receive_forward_message(msg: Message, state: FSMContext):
    data = {
        "message_id": msg.message_id,
        "chat_id": msg.chat.id,
        "is_forwarded": False,
        "source_text": None
    }

    if msg.forward_from_chat:
        # Kanaldan forward qilingan
        data["is_forwarded"] = True
        data["source_text"] = f"📢 Kanal: {msg.forward_from_chat.title}"
    elif msg.forward_from:
        # Foydalanuvchidan forward qilingan
        from_user = msg.forward_from
        name = from_user.full_name
        username = f"@{from_user.username}" if from_user.username else "username yo‘q"
        data["is_forwarded"] = True
        data["source_text"] = f"👤 Foydalanuvchi: {name} ({username})"

    await state.update_data(
        forward_from_message_id=data["message_id"],
        forward_from_chat_id=data["chat_id"],
        is_forwarded=data["is_forwarded"],
        source_text=data["source_text"]
    )

    await state.set_state(AdminManageState.ads_confirm)
    await msg.answer("✅ Xabar qabul qilindi\n\nYuborishni tasdiqlang:", reply_markup=confirm_ad_buttons())

@router.callback_query(AdminManageState.ads_confirm, F.data.in_(["confirm_ads", "cancel_ads", "retry_ads"]))
async def confirm_forward_ads(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()

    msg_id = data.get("forward_from_message_id")
    chat_id = data.get("forward_from_chat_id")
    is_forwarded = data.get("is_forwarded", False)

    if cb.data == "cancel_ads":
        await state.clear()
        await cb.message.delete()
        await cb.message.answer("❌ Reklama yuborish bekor qilindi.", reply_markup=kb_main())
        return

    if cb.data == "retry_ads":
        await state.set_state(AdminManageState.forward_ads)
        await cb.message.delete()
        await cb.message.answer("🔁 Xabarni qayta forward qiling:", reply_markup=cancel_reply_kb())
        return

    if not msg_id or not chat_id:
        await cb.message.delete()
        await cb.message.answer("⚠️ Xatolik: xabar ma’lumotlari topilmadi.", reply_markup=kb_main())
        await state.clear()
        return

    # Barcha foydalanuvchilarni olish
    async with async_session() as session:
        result = await session.execute(select(User.id, User.user_fullname))
        users = result.all()

    if not users:
        await cb.message.delete()
        await cb.message.answer("⚠️ Hech qanday foydalanuvchi topilmadi.", reply_markup=kb_main())
        await state.clear()
        return

    success, failed = 0, 0
    failed_names = []

    for user_id, fullname in users:
        try:
            if is_forwarded:
                await bot.forward_message(chat_id=user_id, from_chat_id=chat_id, message_id=msg_id)
            else:
                await bot.copy_message(chat_id=user_id, from_chat_id=chat_id, message_id=msg_id)
            success += 1
        except Exception:
            failed += 1
            failed_names.append(fullname)

    error_text = (
        f"\n❗ Quyidagilarga yuborilmadi:\n<code>{', '.join(failed_names)}</code>"
        if failed_names else ""
    )

    await cb.message.delete()
    await cb.message.answer(
        f"✅ Reklama yuborildi\n\n"
        f"📬 Muvaffaqiyatli: <b>{success} ta foydalanuvchi</b>\n"
        f"❌ Xatolik: <b>{failed} ta foydalanuvchi</b>"
        f"{error_text}",
        parse_mode="HTML",
        reply_markup=kb_main()
    )
    await state.clear()