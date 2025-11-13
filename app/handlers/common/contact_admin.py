from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
import html

from sqlalchemy import select

from app.database.queries import get_admin_users
from app.states.common_states import ContactAdminState
from app.keyboards.feedback_reply import cancel_reply_kb
from app.keyboards.feedback_inline import (
    to_main_menu_inline,
    user_reply_inline,
    admin_act_inline, FB,
)
from app.utils.text_tools import split_text_by_limit
from app.database.session import async_session
from app.database.models import Feedback, User
from app.database.queries import save_feedback
from app.lib.time import now_tashkent
from app.database.models import Driver
from app.database.queries import get_user_by_id

contact_admin_router = Router(name="contact_admin")

@contact_admin_router.callback_query(F.data == "contact_admin")
async def contact_admin(cb: CallbackQuery, state: FSMContext):
    await state.clear()

    # ⛔ Tekshiramiz: foydalanuvchining javob olinmagan xabari bormi?
    async with async_session() as session:
        existing_fb = await session.execute(
            select(Feedback)
            .where(
                Feedback.user_id == cb.from_user.id,
                Feedback.is_answered.is_(False)
            )
            .order_by(Feedback.created_at.desc())
        )
        pending_feedback = existing_fb.scalar_one_or_none()

    if pending_feedback:
        # Alert ko‘rsatamiz
        await cb.answer(
            "⏳ Sizning oldingi xabaringizga hali javob berilmagan\n\n"
            "Yangi xabar yuborish uchun admin javobini kuting",
            show_alert=True
        )
        return

    await state.set_state(ContactAdminState.writing)

    prompt = await cb.message.answer(
        "<b>✍️ Xabaringizni yozing</b>\n\n"
        "Taklif, savol yoki shikoyatlaringizni yozing — bu xabar adminga bevosita yetkaziladi\n\n"
        "<i>⚠️ Iltimos, fikringizni bir nechta qismlarga bo‘lib yubormang, "
        "barcha maʼlumotni bitta xabarda yozing</i>",
        reply_markup=cancel_reply_kb(),
        parse_mode=ParseMode.HTML
    )
    await state.set_data({"prompt_id": prompt.message_id})
    await cb.answer()

@contact_admin_router.message(ContactAdminState.writing, F.text.casefold() == "❌ bekor qilish")
@contact_admin_router.message(ContactAdminState.admin_answer, F.text.casefold() == "❌ bekor qilish")
async def cancel_feedback(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=to_main_menu_inline(msg.from_user.id),
        parse_mode="HTML"
    )

@contact_admin_router.message(ContactAdminState.writing, F.text)
async def process_feedback(msg: Message, state: FSMContext):

    # Bazaga saqlaymiz
    fb = await save_feedback(
        user_id=msg.from_user.id,
        fullname=msg.from_user.full_name,
        text=msg.text
    )

    await msg.answer("✅ Qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    confirm = await msg.answer(
        "✅ Xabaringiz adminga yuborildi, tez orada javob olasiz!",
        reply_markup=to_main_menu_inline()
    )
    await state.set_state(ContactAdminState.awaiting_menu)
    await state.set_data({"prompt_id": confirm.message_id})

    # Foydalanuvchini bazadan olamiz
    user = await get_user_by_id(msg.from_user.id)

    # Haydovchimi yoki yo‘qmi aniqlaymiz
    from sqlalchemy import select
    from app.database.session import async_session
    async with async_session() as session:
        result = await session.execute(select(Driver).where(Driver.id == user.id))
        is_driver = result.scalar_one_or_none() is not None

    role_display = f"{user.role} (haydovchi)" if is_driver else user.role
    full_text = html.escape(msg.text)
    user: User = await get_user_by_id(msg.from_user.id)
    joined_at_str = user.joined_at.strftime('%d.%m.%Y | %H:%M')

    # Batafsil foydalanuvchi ma’lumotlari
    header = (
        f"<b>📩 Yangi xabar</b>\n\n"
        f"<b>👤 Foydalanuvchi:</b> {html.escape(user.user_fullname)}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>🔗 Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"<b>📞 Telefon:</b> {user.phone_number if user.phone_number else 'yo‘q'}\n"
        f"<b>🎭 Roli:</b> {role_display}\n"
        f"<b>📌 Holati:</b> {'🚫Bloklangan' if user.is_blocked else '✅Faol'}\n"
        f"<b>📅 Qo‘shilgan sana:</b> {joined_at_str}\n\n"
    )
    text_parts = split_text_by_limit(full_text, limit=3500)

    kb = admin_act_inline(
        feedback_id=fb.id,
    )

    # Adminlarga yuborish
    admin_users = await get_admin_users()
    for admin in admin_users:
        for i, part in enumerate(text_parts, 1):
            prefix = (
                f"💬 <b>Xabar matni ({i}/{len(text_parts)}): </b>"
                if len(text_parts) > 1 else "💬 <b>Xabar matni: </b>"
            )
            await msg.bot.send_message(
                chat_id=admin.id,
                text=header + prefix + part,
                reply_markup=kb if i == 1 else None,
                parse_mode=ParseMode.HTML
            )

@contact_admin_router.callback_query(FB.filter(F.action == "reply"))
async def admin_reply_prompt(cb: CallbackQuery, state: FSMContext, callback_data: FB):
    await state.clear()
    await state.set_state(ContactAdminState.admin_answer)
    await state.set_data({"feedback_id": callback_data.fid})

    prompt = await cb.message.answer("✍️ Javob matnini yozing:", reply_markup=cancel_reply_kb())
    await state.update_data(prompt_id=prompt.message_id)
    await cb.answer()

# @contact_admin_router.message(ContactAdminState.admin_answer, F.text)
# async def admin_send_answer(msg: Message, state: FSMContext):
#     from app.database.queries import get_user_by_id
#
#     # 🔐 Admin ekanligini tekshiramiz
#     admin_users = await get_admin_users()
#     if msg.from_user.id not in [admin.id for admin in admin_users]:
#         await state.clear()
#         await msg.answer(
#             "⛔ Siz endi adminlar ro‘yxatida emassiz. Javob yuborish mumkin emas.",
#             reply_markup=to_main_menu_inline()
#         )
#         return
#
#     data = await state.get_data()
#     fid = data.get("feedback_id")
#     if not fid:
#         await state.clear()
#         await msg.answer("⚠️ Muloqot muddati tugagan.")
#         return
#
#     async with async_session() as session:
#         fb: Feedback = await session.get(Feedback, fid)
#
#         # 🔒 Avval javob berilganmi — tekshiramiz
#         if fb.is_answered:
#             from_admin = await get_user_by_id(fb.answered_by)
#
#             if from_admin.id == msg.from_user.id:
#                 await msg.answer(
#                     "❗️ Ushbu foydalanuvchiga allaqachon javob bergansiz",
#                     reply_markup=to_main_menu_inline()
#                 )
#             else:
#                 from_name = html.escape(from_admin.user_fullname)
#                 await msg.answer(
#                     f"❗️ Ushbu foydalanuvchiga allaqachon javob berilgan\n\n"
#                     f"👮‍♂️ <b>Javob bergan admin:</b> {from_name}",
#                     parse_mode=ParseMode.HTML,
#                     reply_markup=to_main_menu_inline()
#                 )
#
#             await state.clear()
#             return
#
#         # ⚙️ Feedbackga javob yoziladi
#         fb.answer_text = msg.text
#         fb.answered_by = msg.from_user.id
#         fb.answered_at = now_tashkent()
#         fb.is_answered = True
#         await session.commit()
#
#     # 👮‍♂️ Admin ma’lumoti
#     admin = await get_user_by_id(msg.from_user.id)
#     admin_name = html.escape(admin.user_fullname)
#
#     # 📨 Foydalanuvchiga yuboriladigan xabar
#     safe_ans = html.escape(msg.text)
#     answer_text = (
#         f"📩 <b>Admin javobi</b>\n\n"
#         f"<b>👮‍♂️ Admin:</b> {admin_name}\n\n"
#         f"<b>💬 Javob matni:</b> {safe_ans}"
#     )
#
#     await msg.bot.send_message(
#         fb.user_id,
#         answer_text,
#         reply_markup=user_reply_inline(),
#         parse_mode=ParseMode.HTML
#     )
#
#     await msg.answer("✅ Qabul qilindi!", reply_markup=ReplyKeyboardRemove())
#     confirm = await msg.answer(
#         "✅ Javob foydalanuvchiga yuborildi.",
#         reply_markup=to_main_menu_inline()
#     )
#     await state.set_state(ContactAdminState.awaiting_menu)
#     await state.set_data({"prompt_id": confirm.message_id})


@contact_admin_router.message(ContactAdminState.admin_answer, F.text)
async def admin_send_answer(msg: Message, state: FSMContext):
    admin_users = await get_admin_users()

    # ⛔ Admin emas
    if msg.from_user.id not in [admin.id for admin in admin_users]:
        await state.clear()
        return await msg.answer(
            "⛔ Siz endi adminlar ro‘yxatida emassiz. Javob yuborish mumkin emas.",
            reply_markup=to_main_menu_inline()
        )

    data = await state.get_data()
    fid = data.get("feedback_id")

    # ⚠️ Foydalanuvchi holati yo‘qolgan
    if not fid:
        await state.clear()
        return await msg.answer("⚠️ Muloqot muddati tugagan.")

    async with async_session() as session:
        fb: Feedback = await session.get(Feedback, fid)

        # ✅ Allaqachon javob berilgan bo‘lsa
        if fb.is_answered:
            from_admin = await get_user_by_id(fb.answered_by)
            from_name = html.escape(from_admin.user_fullname)

            text = (
                "❗️ Ushbu foydalanuvchiga allaqachon javob bergansiz"
                if from_admin.id == msg.from_user.id else
                f"❗️ Ushbu foydalanuvchiga allaqachon javob berilgan\n\n"
                f"👮‍♂️ <b>Javob bergan admin:</b> {from_name}"
            )

            await msg.answer(text, parse_mode=ParseMode.HTML, reply_markup=to_main_menu_inline())
            await state.clear()
            return

        # 🛠️ Javobni saqlash
        fb.answer_text = msg.text
        fb.answered_by = msg.from_user.id
        fb.answered_at = now_tashkent()
        fb.is_answered = True
        await session.commit()

    # ✅ Foydalanuvchiga xabar yuborish
    safe_ans = html.escape(msg.text)

    await msg.bot.send_message(
        fb.user_id,
        (
            f"📩 <b>Admin javobi</b>\n\n"
            f"<b>💬 Javob matni:</b> {safe_ans}"
        ),
        reply_markup=user_reply_inline(),
        parse_mode=ParseMode.HTML
    )

    # 🧾 Adminga tasdiqlovchi xabar
    await msg.answer("✅ Qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    confirm = await msg.answer("✅ Javob foydalanuvchiga yuborildi.", reply_markup=to_main_menu_inline())

    await state.set_state(ContactAdminState.awaiting_menu)
    await state.set_data({"prompt_id": confirm.message_id})

@contact_admin_router.callback_query(FB.filter(F.action == "contact"))
async def contact_private_user(cb: CallbackQuery):
    await cb.answer(
        "⚠️ Foydalanuvchi akkaunti yopiq\n\n"
        "Telegram unga to‘g‘ridan-to‘g‘ri o‘tishga ruxsat bermaydi",
        show_alert=True
    )

@contact_admin_router.callback_query(F.data == "write_again")
async def user_write_again(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ContactAdminState.writing)
    prompt = await cb.message.answer("💬 Yangi xabaringizni kiriting:", reply_markup=cancel_reply_kb())
    await state.set_data({"prompt_id": prompt.message_id})
    await cb.answer()

@contact_admin_router.callback_query(F.data == "to_main")
async def back_to_main(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer(
        "<b>🏠 Asosiy menyu</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=to_main_menu_inline(cb.from_user.id),
        parse_mode="HTML"
    )
    await cb.answer()