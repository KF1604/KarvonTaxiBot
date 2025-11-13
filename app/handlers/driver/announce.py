from datetime import datetime

from app.lib.time import now_tashkent
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from app.database import async_session
from app.database.models import Announcement, Driver, Setting
from app.states.driver_states import DriverAnnouncementState
from app.utils.get_driver_group import get_driver_group_id
from app.keyboards.driver_inline import (
    driver_direction_select_kb,
    confirm_driver_announce_kb,
    to_main_menu_inline,
)
from app.keyboards.driver_reply import cancel_reply_kb
from app.data.viloyatlar import VILOYATLAR2
from app.utils.announce_scheduler import start_announcement_task, stop_announcement_task
from app.keyboards.driver_inline import stop_announce_button


router = Router(name="driver_announce")

# @router.callback_query(F.data == "driver_announce")
# async def start_driver_announce(cb: CallbackQuery, state: FSMContext):
#     allowed, next_time = await is_allowed_to_announce(cb.from_user.id)
#     if not allowed:
#         await cb.answer(
#             "⏳ Siz yaqinda e’lon joylashtirgansiz\n\n"
#             "Har 5 daqiqada faqat bitta e’lon berish mumkin\n\n"
#             f"Yangi e’lonni {next_time} dan keyin joylashtirishingiz mumkin\n\n"
#             "Tushunganingiz uchun rahmat!",
#             show_alert=True
#         )
#         return
#
#     await state.clear()
#     await state.set_state(DriverAnnouncementState.choosing_depart_from)
#     await cb.message.edit_text(
#         "📍 <b>Qayerdan jo‘namoqchisiz?</b>",
#         reply_markup=driver_direction_select_kb(VILOYATLAR2),
#         parse_mode=ParseMode.HTML,
#     )

@router.callback_query(F.data == "driver_announce")
async def start_driver_announce(cb: CallbackQuery, state: FSMContext):
    # ❗ Avval DBdan faol e’lonni tekshiramiz
    async with async_session() as session:
        result = await session.execute(
            select(Announcement).where(
                Announcement.driver_id == cb.from_user.id,
                Announcement.is_active.is_(True)  # faqat faol e’lon
            )
        )
        active_announce = result.scalars().first()  # ✅ xato chiqmaydi

    if active_announce:
        await cb.answer(
            "⚠️ Sizda faol e’lon mavjud\n\n"
            "Yangi e’lon berish uchun avval faol e’lonni yakunlang",
            show_alert=True
        )
        return

    # ✅ Davom etamiz
    await state.clear()
    await state.set_state(DriverAnnouncementState.choosing_depart_from)
    await cb.message.edit_text(
        "📍 <b>Qayerdan jo‘namoqchisiz?</b>",
        reply_markup=driver_direction_select_kb(VILOYATLAR2),
        parse_mode=ParseMode.HTML,
    )

@router.callback_query(DriverAnnouncementState.choosing_depart_from, F.data.startswith("vil_"))
async def select_from_viloyat(cb: CallbackQuery, state: FSMContext):
    from_vil = cb.data.removeprefix("vil_")
    await state.update_data(from_vil=from_vil)
    await state.set_state(DriverAnnouncementState.choosing_arrive_to)
    await cb.message.edit_text(
        f"📍 <b>{from_vil}dan qayerga bormoqchisiz?</b>",
        reply_markup=driver_direction_select_kb(VILOYATLAR2, exclude=from_vil),
        parse_mode=ParseMode.HTML,
    )

@router.callback_query(DriverAnnouncementState.choosing_arrive_to, F.data.startswith("vil_"))
async def select_to_viloyat(cb: CallbackQuery, state: FSMContext):
    to_vil = cb.data.removeprefix("vil_")
    await state.update_data(to_vil=to_vil)
    await state.set_state(DriverAnnouncementState.writing_text)

    await cb.message.edit_text(
        "✅ Yo'nalishlar saqlandi",
        parse_mode=ParseMode.HTML,
    )
    await cb.message.answer("📝 <b>Yo‘nalish bo‘yicha e’lon matnini yuboring</b>", reply_markup=cancel_reply_kb())

@router.message(DriverAnnouncementState.writing_text)
async def save_announce_text(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("⚠️ Faqat matnli xabar yuborishingiz mumkin. Iltimos, matn kiriting")
        return

    data = await state.update_data(text=msg.text)

    preview = f"<b>{data['from_vil']} → {data['to_vil']}</b>\n\n".upper() + data["text"]

    await msg.answer("✅ Matn saqlandi", reply_markup=ReplyKeyboardRemove())

    await msg.answer(
        preview,
        reply_markup=confirm_driver_announce_kb(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(DriverAnnouncementState.confirming)

# @router.callback_query(F.data == "send_driver_announce")
# async def confirm_announce(cb: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     from_vil, to_vil, text = data["from_vil"], data["to_vil"], data["text"]
#
#     async with async_session() as session:
#         result = await session.execute(
#             select(Driver).where(Driver.id == cb.from_user.id)
#         )
#         driver = result.scalar_one_or_none()
#
#         if not driver:
#             await cb.answer("❌ Siz haydovchilar ro‘yxatida mavjud emassiz.", show_alert=True)
#             return
#
#         # 🔍 Bot rejimini tekshiramiz
#         settings = await session.get(Setting, "bot_mode")
#         bot_mode = settings.value if settings else "free"
#
#         now = datetime.now(driver.paid_until.tzinfo) if driver.paid_until else now_tashkent()
#
#         # ✅ Faqat "paid" rejimda to‘lov tekshirilsin
#         if bot_mode == "paid":
#             if not driver.is_paid or not driver.paid_until or driver.paid_until < now:
#                 await cb.answer(
#                 "⚠️ To‘lov muddati tugagan yoki to‘lov amalga oshirilmagan\n\n"
#                     "E’lon berish uchun avval to‘lovni amalga oshiring",
#                         show_alert=True
#                     )
#                 return
#
#     try:
#         group_id = await get_driver_group_id(from_vil, to_vil)
#     except Exception as e:
#         await cb.message.edit_text(f"❌ {e}")
#         await state.clear()
#         return
#
#     announce_text = f"<b>{from_vil} → {to_vil}</b>\n\n".upper() + text
#
#     await cb.bot.send_message(
#         chat_id=group_id,
#         text=announce_text,
#         parse_mode=ParseMode.HTML,
#     )
#
#     async with async_session() as session:
#         session.add(Announcement(
#             driver_id=cb.from_user.id,
#             from_vil=from_vil,
#             to_vil=to_vil,
#             text=text
#         ))
#         await session.commit()
#
#     await cb.message.edit_text(
#         "✅ E’lon guruhga muvaffaqiyatli yuborildi!",
#         reply_markup=announce_sent_success_kb(),
#     )
#     await state.clear()


@router.callback_query(F.data == "send_driver_announce")
async def confirm_announce(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    from_vil, to_vil, text = data["from_vil"], data["to_vil"], data["text"]

    async with async_session() as session:
        result = await session.execute(
            select(Driver).where(Driver.id == cb.from_user.id)
        )
        driver = result.scalar_one_or_none()
        if not driver:
            await cb.answer("❌ Siz haydovchilar ro‘yxatida mavjud emassiz.", show_alert=True)
            return

        # Bot rejimini tekshirish
        settings = await session.get(Setting, "bot_mode")
        bot_mode = settings.value if settings else "free"

        now = datetime.now(driver.paid_until.tzinfo) if driver.paid_until else now_tashkent()
        if bot_mode == "paid":
            if not driver.is_paid or not driver.paid_until or driver.paid_until < now:
                await cb.answer(
                    "⚠️ To‘lov muddati tugagan yoki to‘lov amalga oshirilmagan\n\n"
                    "E’lon berish uchun avval to‘lovni amalga oshiring",
                    show_alert=True
                )
                return

    try:
        group_id = await get_driver_group_id(from_vil, to_vil)
    except Exception as e:
        await cb.message.edit_text(f"❌ {e}")
        await state.clear()
        return

    # E’lon DB ga yoziladi
    async with async_session() as session:
        announcement = Announcement(
            driver_id=cb.from_user.id,
            from_vil=from_vil,
            to_vil=to_vil,
            text=text,
            is_active=True
        )
        session.add(announcement)
        await session.commit()
        await session.refresh(announcement)

    # 🔁 Scheduler ishga tushadi
    start_announcement_task(cb.bot, announcement.id)

    await cb.message.edit_text(
        f"<b>✅ E’lon joylashtirildi!</b>\n\n"
        f"Har 5 daqiqada {from_vil} → {to_vil} guruhiga yuboriladi\n\n"
        f"Iltimos, mijoz topsangiz, quyidagi tugma orqali e’lonni to‘xtating👇",
        reply_markup=stop_announce_button(announcement.id),
    )
    await state.clear()


# ❌ E’lonni tugma orqali to‘xtatish
@router.callback_query(F.data.startswith("stop_announce:"))
async def stop_announce_callback(cb: CallbackQuery):
    ann_id = int(cb.data.split(":")[1])
    await stop_announcement_task(ann_id)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer("E’lon to‘xtatildi ✅")
    await cb.message.answer("<b>✅ E'loningiz muvaffaqiyatli to'xtatildi</b>\n\n"
                            "Yo'lingiz bexatar bo'lsin!\n\n"
                            "Qaytishda yangi e'lon joylashtirishingiz mumkin!")

@router.callback_query(F.data.in_({"edit_driver_announce", "cancel"}))
async def cancel_or_edit(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "❌ E’lon bekor qilindi",
        reply_markup=to_main_menu_inline(),
    )