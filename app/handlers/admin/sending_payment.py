import asyncio
from datetime import timedelta, datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, or_, and_
from app.database.queries import get_unpaid_drivers, set_bot_mode, get_driver_by_id
from app.keyboards.admin_inline import admin_menu_buttons
from app.lib.time import now_tashkent
from app.states.click_states import AccessStates, PaymentDeleteState
import logging
import sys
from os import getenv
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
from aiogram import Bot, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, LabeledPrice, PreCheckoutQuery,
    CallbackQuery
)
from app.database.models import Payment, Driver, Setting  # Import model
from app.database.session import async_session  # SQLAlchemy session

router = Router(name="sending")

load_dotenv()

class Env:
    BOT_TOKEN: str = getenv("API_TOKEN")
    CLICK_TOKEN: str = getenv("CLICK_TOKEN")
    PAYME_TOKEN: str = getenv("PAYME_TOKEN")

env = Env()

# Validate tokens at startup
if not env.BOT_TOKEN or not env.CLICK_TOKEN:
    logging.error("Missing TOKEN or CLICK_TOKEN environment variables")
    sys.exit(1)

# --- Bot ---
bot = Bot(
    token=env.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Constants
AMOUNT_SO_M = 50_000  # so'm
DEADLINE_DAYS = 3

@router.callback_query(F.data.startswith("confirm_bot_mode:"))
async def confirm_change(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccessStates.send_all)
    new_mode = callback.data.split(":")[1]
    await set_bot_mode(new_mode)

    await callback.message.edit_text(
        f"✅ Bot rejimi muvaffaqiyatli o‘zgartirildi.\nYangi rejim: <b>{'Pullik' if new_mode == 'paid' else 'Bepul'}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_menu_buttons("owner")
    )
    if new_mode == "paid":
        deadline = now_tashkent() + timedelta(days=DEADLINE_DAYS)
        await send_payment_reminder(amount=AMOUNT_SO_M, deadline=deadline)

# --- Reminder ---
async def send_payment_reminder(amount: int, deadline: datetime):
    unpaid_drivers = await get_unpaid_drivers()

    if not unpaid_drivers:
        logging.info("📭 To‘lov qilmagan haydovchilar topilmadi.")
        return

    for driver in unpaid_drivers:
        text = (
            f"📢 Hurmatli <b>{driver.fullname}</b>!\n\n"
            "Siz foydalanayotgan <b>Karvon Taxi</b> bot endilikda <b>pullik rejimga o‘tdi</b>.\n\n"
            "🛠 Ushbu tizim siz kabi haydovchilar uchun qulay va tezkor xizmat ko‘rsatish maqsadida yaratilgan. "
            "Botni ishlab chiqish, qo‘llab-quvvatlash va doimiy rivojlantirish katta mehnat, vaqt va mablag‘ "
            "talab qiladi.\n\n"
            "🎯 Xizmatlar sifatini saqlab qolish va rivojlantirishni davom ettirish maqsadida "
            "<b>oylik to‘lov tizimi</b> joriy qilindi.\n\n"
            f"💰 To‘lov miqdori: <b>{amount:,} (ellik ming) so‘m</b>\n"
            f"⏳ To‘lov uchun oxirgi muddat: <b>{deadline.strftime('%d.%m.%Y | %H:%M')}</b>\n\n"
            "❗️ Iltimos, <b>3 kun</b> ichida to‘lovni amalga oshiring\n"
            "Aks holda sizning bot xizmatlaringiz cheklanadi va haydovchilar guruhidan chiqarib yuborilasiz\n\n"
        )
        kb = InlineKeyboardBuilder()
        kb.button(text="To'lov qilish (Click)", callback_data="tolash_click")
        kb.adjust(1)

        try:
            await bot.send_message(driver.id, text, reply_markup=kb.as_markup())
            logging.info(f"📩 Xabar yuborildi: {driver.id}")
        except Exception as e:
            logging.warning(f"❌ Xabar yuborilmadi: {driver.id} — {e}")

            # Telegram rate-limit uchun — 1 sekundda ~16 ta xabar
        await asyncio.sleep(0.06)

async def send_1day_left_warning(bot: Bot, amount: int = 50000):
    now = now_tashkent()
    warning_time = now + timedelta(days=1)

    async with async_session() as session:
        settings = await session.get(Setting, "bot_mode")
        if not settings or settings.value != "paid":
            return

    async with async_session() as session:
        result = await session.execute(
            select(Driver).where(
                (Driver.is_paid == False) &
                (Driver.paid_until <= warning_time) &
                (Driver.paid_until > now)
            )
        )
        drivers = result.scalars().all()

        for driver in drivers:
            text = (
                f"⚠️ <b>Diqqat! Xizmat muddati yakunlanmoqda</b>\n\n"
                f"Hurmatli <b>{driver.fullname}</b>\n\n"
                f"Sizning pullik xizmatlardan foydalanish muddati tugashiga <b>1 kun</b> qoldi\n\n"
                f"💰 To‘lov miqdori: <b>{amount:,} (ellik ming) so‘m</b>\n"
                f"⏳ Amal qilish muddati: <b>{driver.paid_until.strftime('%d.%m.%Y | %H:%M')}</b>\n\n"
                f"Iltimos, belgilangan muddat ichida to‘lovni amalga oshiring\n"
                f"Aks holda sizning bot xizmatlaringiz cheklanadi va guruhdan avtomatik tarzda chiqarib yuborilasiz"
            )
            kb = InlineKeyboardBuilder()
            kb.button(text="To'lov qilish (Click)", callback_data="tolash_click")
            kb.adjust(1)

            try:
                await bot.send_message(chat_id=driver.id, text=text, reply_markup=kb.as_markup())
                logging.info(f"🔔 Ogohlantirish yuborildi: {driver.id}")
            except Exception as e:
                logging.warning(f"❌ Xabar yuborilmadi: {driver.id} — {e}")

            await asyncio.sleep(0.06)

@router.callback_query(lambda c: c.data in ["tolash_click"])
async def cmd_buy(cb: CallbackQuery,state:FSMContext):
    await cb.message.edit_text("ᅠ", reply_markup=None)
    provider = cb.data.split("_")[1]

    provider_name = "Click" if provider == "click" else "Payme"

    prices = [LabeledPrice(label="Oylik to‘lov", amount=AMOUNT_SO_M * 100)]

    delete_message = await cb.message.answer_invoice(
        title=f"Oylik obuna",
        description=f"{provider_name} orqali to‘lov qilish uchun quyidagi tugmani bosing",
        payload=f"{cb.from_user.id}_{provider_name.lower()}",
        provider_token=env.CLICK_TOKEN,
        currency="UZS",
        prices=prices,
        photo_url="https://i.imgur.com/GkBDjVj.png",
        photo_width=800,
        photo_height=650,
        is_flexible=False,
    )
    await state.set_state(PaymentDeleteState.message_id)
    await state.update_data(inline_msg_id=delete_message.message_id)

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(lambda msg: msg.successful_payment is not None)
async def on_successful_payment(message: Message,state:FSMContext):
    data = await state.get_data()
    message_id = data.get("inline_msg_id")
    pay = message.successful_payment
    payload_parts = pay.invoice_payload.split("_")
    user_id = int(payload_parts[0])
    provider_used = payload_parts[1] if len(payload_parts) > 1 else "unknown"
    amount = pay.total_amount // 100

    async with async_session() as session:
        driver = await get_driver_by_id(session, user_id)
        if driver:
            await bot.delete_message(message.chat.id,message_id=message_id)

            driver.is_paid = True

            now = now_tashkent()
            base_time = driver.paid_until if driver.paid_until and driver.paid_until > now else now
            new_paid_until = base_time + relativedelta(months=1)
            driver.paid_until = new_paid_until

            payment = Payment(
                driver_id=driver.id,
                amount=amount,
                payment_id=pay.invoice_payload + f"-{now.timestamp()}",
                status="success",
                provider=provider_used
            )
            session.add(payment)
            await session.commit()
            await message.answer(
                f"Hurmatli <b>{driver.fullname}</b>!\n\n"
                f"Sizning toʻlovingiz <b>{provider_used.title()}</b> orqali muvaffaqiyatli amalga oshirildi! ✅\n"
                f"Endilikda siz botdagi barcha xizmatlardan toʻliq foydalana olasiz!\n\n"
                f"💵 Toʻlangan summa: <b>{amount:,} (ellik ming) {pay.currency}</b>\n"
                f"🗓 Obuna muddati: <b>{new_paid_until.strftime('%d.%m.%Y | %H:%M')} gacha</b>\n\n"
                f"🚘 Safarlaringiz serdaromad, yo'llaringiz bexatar bo'lsin!\n"
            )
        else:
            await message.answer("❗Foydalanuvchi bazada topilmadi")


# BATCH_SIZE = 200
#
# async def remove_expired_drivers(bot: Bot):
#     now = now_tashkent()
#
#     async with async_session() as session:
#         # 1. Bot rejimini tekshirish
#         settings = await session.get(Setting, "bot_mode")
#         if not settings or settings.value != "paid":
#             return
#
#         # 2. O‘chirilishi kerak bo‘lgan haydovchilarni olish
#         result = await session.execute(
#             select(Driver)
#             .where(
#                 (Driver.is_paid == False) |
#                 (Driver.paid_until < now)
#             )
#             .limit(BATCH_SIZE)
#         )
#         unpaid_drivers = result.scalars().all()
#
#         if not unpaid_drivers:
#             logging.info("⚠️ To‘lov muddati o‘tgan haydovchilar topilmadi")
#             return
#
#         removed_count = 0
#
#         # 3. Har bir haydovchini asinxron tarzda qayta ishlash
#         async def process_driver(driver: Driver):
#             nonlocal removed_count
#             for group_id in driver.group_chat_ids:
#                 try:
#                     await bot.ban_chat_member(group_id, driver.id)
#                     await bot.unban_chat_member(group_id, driver.id)
#                     logging.info(f"🚫 Haydovchi {driver.id} guruhdan chiqarildi: {group_id}")
#                     await asyncio.sleep(0.6)  # API limitdan o‘tmaslik uchun
#                 except TelegramBadRequest as e:
#                     # Masalan, guruh mavjud emas yoki user allaqachon yo‘q
#                     logging.warning(f"⚠️ Haydovchi {driver.id} guruhdan chiqarilmadi ({group_id}): {e}")
#                 except Exception as e:
#                     logging.error(f"❌ Guruhdan chiqarishda xatolik: {driver.id} - {group_id}: {e}")
#
#             try:
#                 await session.delete(driver)
#                 removed_count += 1
#             except Exception as e:
#                 logging.error(f"❌ DB dan haydovchini o‘chirishda xatolik: {driver.id} - {e}")
#
#         # 4. Parallel ishlash
#         await asyncio.gather(*(process_driver(d) for d in unpaid_drivers))
#
#         # 5. O‘zgarishlarni saqlash
#         await session.commit()
#         logging.info(f"🧾 Jami o‘chirilgan haydovchilar: {removed_count}")


BATCH_SIZE = 200
MAX_PARALLEL = 10   # Bir vaqtda faqat 10 ta haydovchi ishlansin

async def remove_expired_drivers(bot: Bot):
    now = now_tashkent()

    async with async_session() as session:
        # 1. Bot rejimini tekshirish
        settings = await session.get(Setting, "bot_mode")
        if not settings or settings.value != "paid":
            return

        # 2. To‘lov muddati o‘tgan haydovchilarni olish
        result = await session.execute(
            select(Driver).where(
                or_(
                    # 1) To‘lov qilmagan va muddati tugagan
                    and_(Driver.is_paid == False, Driver.paid_until < now),
                    # 2) To‘lov qilgan, lekin muddati tugagan
                    and_(Driver.is_paid == True, Driver.paid_until < now),
                    # 3) Umuman paid_until qo‘yilmagan (yangi yoki noto‘liq foydalanuvchi)
                    Driver.paid_until == None
                )
            ).limit(BATCH_SIZE)
        )
        unpaid_drivers = result.scalars().all()

        if not unpaid_drivers:
            logging.info("⚠️ To‘lov muddati o‘tgan haydovchilar topilmadi")
            return

        removed_count = 0
        sem = asyncio.Semaphore(MAX_PARALLEL)  # Parallelizm cheklovi

        async def process_driver(driver: Driver):
            nonlocal removed_count
            async with sem:
                for group_id in getattr(driver, "group_chat_ids", []):
                    try:
                        await bot.ban_chat_member(group_id, driver.id)
                        await bot.unban_chat_member(group_id, driver.id)
                        logging.info(f"🚫 Haydovchi {driver.id} guruhdan chiqarildi: {group_id}")
                        await asyncio.sleep(0.5)  # API flood limitni buzmaslik uchun
                    except TelegramBadRequest as e:
                        logging.warning(f"⚠️ Haydovchi {driver.id} ({group_id}) chiqarilmadi: {e}")
                    except Exception as e:
                        logging.error(f"❌ Guruhdan chiqarishda xatolik {driver.id} ({group_id}): {e}")

                removed_count += 1

        # 3. Parallel ishlash
        await asyncio.gather(*(process_driver(d) for d in unpaid_drivers))

        # 4. Bulk delete (birdaniga o‘chirish)
        for d in unpaid_drivers:
            await session.delete(d)

        # 5. Commit qilish
        await session.commit()
        logging.info(f"🧾 Jami o‘chirilgan haydovchilar: {removed_count}")