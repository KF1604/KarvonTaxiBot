# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
# from aiogram.fsm.context import FSMContext
#
# from app.keyboards.parcel_inline import (
#     viloyat_buttons, tuman_buttons,
#     confirm_keyboard, to_main_menu_inline,
#     contact_client_button
# )
# from app.keyboards.parcel_reply import phone_keyboard, location_keyboard, comment_keyboard
# from app.data.viloyatlar import VILOYATLAR
# from app.states.parcel_states import ParcelState
# from app.database.queries import save_order
# from app.utils.filters import TextOnlyWithWarning
# from app.utils.get_group import get_group_id
# from app.utils.helpers import normalize_phone
# from app.utils.rate_limiter import is_allowed_to_order
#
# parcel_router = Router(name="parcel")
#
# @parcel_router.callback_query(F.data == "order_parcel")
# async def start_parcel_callback(call: CallbackQuery, state: FSMContext):
#
#     allowed, next_time = await is_allowed_to_order(user_id=call.from_user.id)
#     if not allowed:
#         await call.answer(
#             f"⏳ Siz yaqinda buyurtma bergansiz\n\n"
#             f"Har 5 daqiqada faqat bitta buyurtma berish mumkin\n\n"
#             f"{next_time} dan keyin qayta urinib ko‘ring\n\n"
#             f"Tushunganingiz uchun rahmat!",
#             show_alert=True
#         )
#         return
#
#     await state.clear()
#     await state.set_state(ParcelState.choose_from_viloyat)
#     await call.message.edit_text(
#         "<b>📦 Jo'natma qaysi viloyatdan yuboriladi?</b>",
#         reply_markup=viloyat_buttons(list(VILOYATLAR.keys()))
#     )
#     await call.answer()
#
# @parcel_router.callback_query(ParcelState.choose_from_viloyat, F.data.startswith("viloyat_"))
# async def from_viloyat(call: CallbackQuery, state: FSMContext):
#     vil = call.data.removeprefix("viloyat_")
#     await state.update_data(from_viloyat=vil)
#
#     await call.message.edit_text(
#         f"<b>📦 {vil}ning qaysi tumanidan yuboriladi?</b>",
#         reply_markup=tuman_buttons(VILOYATLAR[vil]),
#         parse_mode="HTML"
#     )
#     await state.set_state(ParcelState.choose_from_tuman)
#     await call.answer()
#
# @parcel_router.callback_query(ParcelState.choose_from_tuman, F.data.startswith("tuman_"))
# async def from_tuman(call: CallbackQuery, state: FSMContext):
#     await state.update_data(from_tuman=call.data.removeprefix("tuman_"))
#     fv = (await state.get_data()).get("from_viloyat")
#     vil_list = [v for v in VILOYATLAR if v != fv]
#     await call.message.edit_text(
#         "<b>📦 Jo'natma qaysi viloyatga yuboriladi?</b>",
#         reply_markup=viloyat_buttons(vil_list),
#     )
#     await state.set_state(ParcelState.choose_to_viloyat)
#     await call.answer()
#
# @parcel_router.callback_query(ParcelState.choose_to_viloyat, F.data.startswith("viloyat_"))
# async def to_viloyat(call: CallbackQuery, state: FSMContext):
#     vil = call.data.removeprefix("viloyat_")
#     await state.update_data(to_viloyat=vil)
#
#     await call.message.edit_text(
#         f"<b>📦 {vil}ning qaysi tumaniga yuboriladi?</b>",
#         reply_markup=tuman_buttons(VILOYATLAR[vil]),
#         parse_mode="HTML"
#     )
#     await state.set_state(ParcelState.choose_to_tuman)
#     await call.answer()
#
# @parcel_router.callback_query(ParcelState.choose_to_tuman, F.data.startswith("tuman_"))
# async def to_tuman(call: CallbackQuery, state: FSMContext):
#     tuman = call.data.split("_", 1)[1]
#     await state.update_data(to_tuman=tuman)
#     await state.set_state(ParcelState.choose_time)
#     await call.message.edit_text(
#         "<b>🕒 Jo‘natma yuborish vaqtini kiriting</b>\n\n"
#         "<b>Misol uchun</b>: <code>Ertaga soat 9:00 da</code>",
#         parse_mode="HTML"
#     )
#     await call.answer()
#
# # 5. Vaqt kiritish (faqat qo‘lda yozilgan matn)
# @parcel_router.message(ParcelState.choose_time, TextOnlyWithWarning())
# async def input_time(message: Message, state: FSMContext):
#     await state.update_data(parcel_time=message.text.strip())
#     await state.set_state(ParcelState.choose_phone)
#     await message.answer("📞 Telefon raqamingizni yuboring", reply_markup=phone_keyboard())
#
# # 6. Telefon raqamni tekshirish
# @parcel_router.message(ParcelState.choose_phone)
# async def input_phone(message: Message, state: FSMContext):
#     # 1) Kontakt yuborilgan bo‘lsa
#     if message.contact and message.contact.phone_number:
#         phone = normalize_phone(message.contact.phone_number)
#
#     # 2) Matn ko‘rinishida raqam yuborilgan bo‘lsa
#     elif message.text:
#         phone = normalize_phone(message.text.strip())
#
#     # 3) Aks holda (media, sticker, emoji, video, voice...) – rad etiladi
#     else:
#         await message.answer(
#             "⚠️ Iltimos, faqat telefon raqam yuboring",
#             reply_markup=phone_keyboard()
#         )
#         return
#
#     # Telefon raqam noto‘g‘ri formatda bo‘lsa
#     if phone is None:
#         await message.answer(
#             "<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
#             "Raqamni quyidagilardan birida yuboring:\n"
#             "• <code>+998901234567</code>\n"
#             "• <code>998901234567</code>\n"
#             "• <code>901234567</code>\n\n"
#             "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>",
#             reply_markup=phone_keyboard()
#         )
#         return
#
#     # ✅ Ma'lumotni saqlaymiz, keyingi bosqichga o‘tamiz
#     await state.update_data(phone_number=phone)
#     await state.set_state(ParcelState.choose_location)
#     await message.answer("📍 Geo‑joylashuvingizni yuboring", reply_markup=location_keyboard())
#
# @parcel_router.message(ParcelState.choose_location)
# async def input_location(message: Message, state: FSMContext):
#     if not message.location:
#         await message.answer("⚠️ Faqat quyidagi tugmalardan foydalaning!")
#         return
#     lat, lon = message.location.latitude, message.location.longitude
#     geo_link = f"https://maps.google.com/?q={lat},{lon}"
#     await state.update_data(location_link=geo_link)
#     await state.set_state(ParcelState.choose_comment)
#     await message.answer(
#         "<b>💬 Yuk haqida izoh qoldiring</b>\n\n"
#         "Yukning soni, hajmi yoki boshqa muhim ma’lumotlarni yozing. Bu sizga mos haydovchi topilishiga yordam beradi.\n\n"
#         "<b>Misollar:</b>\n"
#         "• <code>2 ta sumka, 5 kg</code>\n"
#         "• <code>1 ta katta quti, taxminan 15 kg</code>\n"
#         "• <code>3 ta o‘rtacha sumka, sinadigan narsa bor</code>\n"
#         "• <code>1 ta velosiped, 'rack' kerak</code>\n\n"
#         "Iltimos, faqat kerakli ma’lumotlarni yozing 👇",
#         reply_markup=comment_keyboard()
#     )
#
# @parcel_router.message(ParcelState.choose_comment, TextOnlyWithWarning())
# async def input_comment(message: Message, state: FSMContext):
#     comment = None if message.text == "⏭️ O‘tkazib yuborish" else message.text.strip()
#     await state.update_data(comment=comment)
#     await state.set_state(ParcelState.confirm)
#
#     d = await state.get_data()
#     confirm_text = (
#         "<b>⚠️Buyurtmangizni tasdiqlang:</b>\n\n"
#         "<b>Buyurtma turi:</b> 📦 Jo‘natma yuborish\n"
#         f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
#         f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
#         f"<b>🕒 Vaqti:</b> {d.get('parcel_time') or 'kiritilmagan'}\n"
#         f"<b>📞 Telefon raqamingiz:</b> {d.get('phone_number') or 'kiritilmagan'}\n"
#         f"<b>📍 Geo-joylashuvingiz:</b> {d['location_link']}\n\n"
#         f"<b>💬 Haydovchiga izoh:</b> {d.get('comment') or 'yo‘q'}"
#     )
#
#     await message.answer("✅ Ma'lumotlar qabul qilindi!", reply_markup=ReplyKeyboardRemove())
#     await message.answer(confirm_text, reply_markup=confirm_keyboard(), parse_mode="HTML", disable_web_page_preview=True)
#
# @parcel_router.callback_query(ParcelState.confirm, F.data == "confirm_order")
# async def step_confirm(call: CallbackQuery, state: FSMContext):
#     d = await state.get_data()
#
#     await save_order(
#         user_fullname=call.from_user.full_name,
#         user_id=call.from_user.id,
#         order_type="jo'natma",
#         from_viloyat=d["from_viloyat"],
#         from_district=d["from_tuman"],
#         to_viloyat=d["to_viloyat"],
#         to_district=d["to_tuman"],
#         time=d["parcel_time"],
#         phone=d.get("phone_number"),
#         location=d["location_link"],
#         comment_to_driver=d.get("comment"),
#     )
#
#     await call.message.edit_text(
#         "<b>✅ Buyurtmangiz qabul qilindi!</b>\n\n"
#         "Haydovchilarimiz tez orada siz bilan bog‘lanishadi!\n\n"
#         "Bizning xizmatimizdan foydalanganingiz uchun tashakkur!",
#         reply_markup=to_main_menu_inline(),
#         parse_mode="HTML"
#     )
#
#     group_id = await get_group_id(d["from_viloyat"], d["to_viloyat"])
#     await call.bot.send_message(
#         group_id,
#         text=(
#             "<b>💥 Yangi buyurtma!</b>\n\n"
#             "<b>Buyurtma turi:</b> 📦 Jo‘natma\n"
#             f"<b>👤 Mijoz:</b> {call.from_user.full_name}\n"
#             f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
#             f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
#             f"<b>🕒 Vaqti:</b> {d.get('parcel_time') or 'kiritilmagan'}\n"
#             f"<b>📞 Mijoz raqami:</b> {d.get('phone_number') or 'kiritilmagan'}\n"
#             f"<b>📍 Geo-joylashuvi:</b> {d['location_link']}\n\n"
#             f"<b>💬 Izoh:</b> <i>{d.get('comment') or 'yo‘q'}</i>"
#         ),
#         reply_markup=contact_client_button(
#             user_id=call.from_user.id,
#             username=call.from_user.username
#         ),
#         parse_mode="HTML",
#         disable_web_page_preview = True
#     )
#
#     await state.clear()
#     await call.answer()
#
#
#



from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from app.keyboards.parcel_inline import (
    viloyat_buttons, tuman_buttons,
    confirm_keyboard, to_main_menu_inline,
    contact_client_button, order_for_whom_buttons2
)
from app.keyboards.parcel_reply import phone_keyboard, location_keyboard, comment_keyboard
from app.data.viloyatlar import VILOYATLAR
from app.states.parcel_states import ParcelState
from app.database.queries import save_order
from app.utils.filters import TextOnlyWithWarning
from app.utils.get_group import get_group_id
from app.database.queries import get_user_phone
from app.utils.helpers import normalize_phone
from app.utils.rate_limiter import is_allowed_to_order

parcel_router = Router(name="parcel")

@parcel_router.callback_query(F.data == "order_parcel")
async def start_parcel_callback(call: CallbackQuery, state: FSMContext):
    allowed, next_time = await is_allowed_to_order(user_id=call.from_user.id)
    if not allowed:
        await call.answer(
            f"⏳ Siz yaqinda buyurtma bergansiz\n\n"
            f"Har 5 daqiqada faqat bitta buyurtma berish mumkin\n\n"
            f"{next_time} dan keyin qayta urinib ko‘ring\n\n"
            f"Tushunganingiz uchun rahmat!",
            show_alert=True
        )
        return

    await state.clear()
    await state.set_state(ParcelState.choose_for_whom)
    await call.message.edit_text(
        "<b>📦 Jo'natma yuborish bo'limi</b>\n\nJo'natmani kim yuboradi?",
        reply_markup=order_for_whom_buttons2()
    )
    await call.answer()

@parcel_router.callback_query(ParcelState.choose_for_whom)
async def choose_for_whom(call: CallbackQuery, state: FSMContext):
    choice = "self" if call.data == "order_for_me" else "friend"
    await state.update_data(for_whom=choice)

    await call.message.edit_text(
        "<b>📦 Jo'natma qaysi viloyatdan yuboriladi?</b>",
        reply_markup=viloyat_buttons(list(VILOYATLAR.keys()))
    )
    await state.set_state(ParcelState.choose_from_viloyat)
    await call.answer()

@parcel_router.callback_query(ParcelState.choose_from_viloyat, F.data.startswith("viloyat_"))
async def from_viloyat(call: CallbackQuery, state: FSMContext):
    vil = call.data.removeprefix("viloyat_")
    await state.update_data(from_viloyat=vil)

    await call.message.edit_text(
        f"<b>📦 {vil}ning qaysi tumanidan yuboriladi?</b>",
        reply_markup=tuman_buttons(VILOYATLAR[vil]),
        parse_mode="HTML"
    )
    await state.set_state(ParcelState.choose_from_tuman)
    await call.answer()

@parcel_router.callback_query(ParcelState.choose_from_tuman, F.data.startswith("tuman_"))
async def from_tuman(call: CallbackQuery, state: FSMContext):
    await state.update_data(from_tuman=call.data.removeprefix("tuman_"))
    fv = (await state.get_data()).get("from_viloyat")
    vil_list = [v for v in VILOYATLAR if v != fv]
    await call.message.edit_text(
        "<b>📦 Jo'natma qaysi viloyatga yuboriladi?</b>",
        reply_markup=viloyat_buttons(vil_list),
    )
    await state.set_state(ParcelState.choose_to_viloyat)
    await call.answer()

@parcel_router.callback_query(ParcelState.choose_to_viloyat, F.data.startswith("viloyat_"))
async def to_viloyat(call: CallbackQuery, state: FSMContext):
    vil = call.data.removeprefix("viloyat_")
    await state.update_data(to_viloyat=vil)

    await call.message.edit_text(
        f"<b>📦 {vil}ning qaysi tumaniga yuboriladi?</b>",
        reply_markup=tuman_buttons(VILOYATLAR[vil]),
        parse_mode="HTML"
    )
    await state.set_state(ParcelState.choose_to_tuman)
    await call.answer()

@parcel_router.callback_query(ParcelState.choose_to_tuman, F.data.startswith("tuman_"))
async def to_tuman(call: CallbackQuery, state: FSMContext):
    tuman = call.data.split("_", 1)[1]
    await state.update_data(to_tuman=tuman)
    await state.set_state(ParcelState.choose_time)
    await call.message.edit_text(
        "<b>🕒 Jo‘natma yuborish vaqtini kiriting</b>\n\n"
        "<b>Misol uchun</b>: <code>Ertaga soat 9:00 da</code>",
        parse_mode="HTML"
    )
    await call.answer()

# 5. Vaqt kiritish (faqat qo‘lda yozilgan matn)
@parcel_router.message(ParcelState.choose_time, TextOnlyWithWarning())
async def input_time(message: Message, state: FSMContext):
    await state.update_data(parcel_time=message.text.strip())
    data = await state.get_data()

    # 🧾 Tanishi uchun — telefon raqami so‘raladi
    if data.get("for_whom") == "friend":
        await state.set_state(ParcelState.choose_phone)
        return await message.answer("📞 Tanishingizning telefon raqamini yuboring", reply_markup=phone_keyboard())

    # 🧾 Aks holda (o‘zi uchun) — telefon bazadan olinadi
    phone = await get_user_phone(message.from_user.id)

    next_state = ParcelState.choose_location
    await state.update_data(phone_number=phone if phone else None)
    await state.set_state(ParcelState.choose_phone if not phone else next_state)

    await message.answer(
        "📍 Geo‑joylashuvingizni yuboring" if phone else "📞 Telefon raqamingizni yuboring",
        reply_markup=location_keyboard() if phone else phone_keyboard()
    )
# 6. Telefon raqamni tekshirish
@parcel_router.message(ParcelState.choose_phone)
async def input_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    for_whom = data.get("for_whom")
    user_id = message.from_user.id

    # 📲 Telefon raqamini aniqlash
    raw_phone = (
        message.contact.phone_number if message.contact and message.contact.phone_number
        else message.text.strip() if message.text
        else None
    )

    phone = normalize_phone(raw_phone) if raw_phone else None

    # ❌ Telefon raqam noto‘g‘ri bo‘lsa
    if not phone:
        return await message.answer(
            "<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
            "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>",
            reply_markup=phone_keyboard()
        )

    # 🔐 Agar tanishi uchun bo‘lsa, o‘z raqamiga ruxsat yo‘q
    if for_whom == "friend":
        user_phone = await get_user_phone(user_id)
        if user_phone and normalize_phone(user_phone) == phone:
            return await message.answer(
                "<b>⚠️ Ushbu raqam sizga tegishli</b>\n\n"
                "Iltimos, tanishingizga tegishli raqamni kiriting",
                reply_markup=phone_keyboard()
            )

    # ✅ Raqam qabul qilindi, davom etamiz
    await state.update_data(phone_number=phone)
    await state.set_state(ParcelState.choose_location)

    location_msg = (
        "📍 Tanishingizning geo‑joylashuvini yuboring"
        if for_whom == "friend" else
        "📍 Geo‑joylashuvingizni yuboring"
    )

    await message.answer(location_msg, reply_markup=location_keyboard())

@parcel_router.message(ParcelState.choose_location)
async def input_location(message: Message, state: FSMContext):
    if not message.location:
        await message.answer("⚠️ Iltimos, faqat tugmadan foydalaning!")
        return
    lat, lon = message.location.latitude, message.location.longitude
    geo_link = f"https://maps.google.com/?q={lat},{lon}"
    await state.update_data(location_link=geo_link)
    await state.set_state(ParcelState.choose_comment)
    await message.answer(
        "<b>💬 Yuk haqida izoh qoldiring</b>\n\n"
        "Yukning soni, hajmi yoki boshqa muhim ma’lumotlarni yozing. Bu sizga mos haydovchi topilishiga yordam beradi.\n\n"
        "<b>Misollar:</b>\n"
        "• <code>2 ta sumka, 5 kg</code>\n"
        "• <code>1 ta katta quti, taxminan 15 kg</code>\n"
        "• <code>3 ta o‘rtacha sumka, sinadigan narsa bor</code>\n"
        "• <code>1 ta velosiped, 'rack' kerak</code>\n\n"
        "Iltimos, faqat kerakli ma’lumotlarni yozing 👇",
        reply_markup=comment_keyboard()
    )

@parcel_router.message(ParcelState.choose_comment, TextOnlyWithWarning())
async def input_comment(message: Message, state: FSMContext):
    comment = None if message.text == "⏭️ O‘tkazib yuborish" else message.text.strip()
    await state.update_data(comment=comment)

    d = await state.get_data()

    # Agar o‘zi uchun bo‘lsa, telefon raqamni Users jadvalidan olib qo‘yamiz
    if d.get("for_whom") != "friend":
        phone = await get_user_phone(message.from_user.id)
        if phone:
            await state.update_data(phone_number=phone)

    await state.set_state(ParcelState.confirm)

    # Qaysi uchun: "O‘zim" yoki "Tanishim"
    is_for_friend = d.get("for_whom") == "friend"
    phone_text = d.get("phone_number") or "kiritilmagan"
    client_label = "📞 Tanishingizning raqami" if is_for_friend else "📞 Telefon raqamingiz"

    confirm_text = (
        "<b>⚠️Buyurtmangizni tasdiqlang:</b>\n\n"
        "<b>Buyurtma turi:</b> 📦 Jo‘natma yuborish\n"
        f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
        f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
        f"<b>🕒 Vaqti:</b> {d.get('parcel_time') or 'kiritilmagan'}\n"
        f"<b>{client_label}:</b> {phone_text}\n"
        f"<b>📍 Geo-joylashuv:</b> {d['location_link']}\n\n"
        f"<b>💬 Haydovchiga izoh:</b> {d.get('comment') or 'yo‘q'}"
    )

    await message.answer("✅ Ma'lumotlar qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    await message.answer(confirm_text, reply_markup=confirm_keyboard(), parse_mode="HTML",
                         disable_web_page_preview=True)

@parcel_router.callback_query(ParcelState.confirm, F.data == "confirm_order")
async def step_confirm(call: CallbackQuery, state: FSMContext):
    d = await state.get_data()

    await save_order(
        user_fullname=call.from_user.full_name,
        user_id=call.from_user.id,
        order_type="jo'natma",
        from_viloyat=d["from_viloyat"],
        from_district=d["from_tuman"],
        to_viloyat=d["to_viloyat"],
        to_district=d["to_tuman"],
        time=d["parcel_time"],
        phone=d.get("phone_number"),
        location=d["location_link"],
        comment_to_driver=d.get("comment"),
    )

    await call.message.edit_text(
        "<b>✅ Buyurtmangiz qabul qilindi!</b>\n\n"
        "Haydovchilarimiz tez orada siz bilan bog‘lanishadi!\n\n"
        "Bizning xizmatimizdan foydalanganingiz uchun tashakkur!",
        reply_markup=to_main_menu_inline(),
        parse_mode="HTML"
    )

    # 📤 Guruhga yuborish
    group_id = await get_group_id(d["from_viloyat"], d["to_viloyat"])
    is_for_friend = d.get("for_whom") == "friend"
    client_name = call.from_user.full_name
    phone_text = d.get("phone_number") or "kiritilmagan"

    group_text = (
        "<b>💥 Yangi buyurtma!</b>\n\n"
        "<b>Buyurtma turi:</b> 📦 Jo‘natma\n"
        f"<b>👤 Mijoz:</b> {client_name}\n"
        f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
        f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
        f"<b>🕒 Vaqti:</b> {d.get('depart_time') or 'kiritilmagan'}\n"
        f"<b>📞 {'Tanishining raqami' if is_for_friend else 'Mijoz raqami'}:</b> {phone_text}\n"
        f"<b>📍 Geo-joylashuv:</b> {d['location_link']}\n\n"
        f"<b>💬 Izoh:</b> <i>{d.get('comment') or 'yo‘q'}</i>"
    )

    reply_markup = None
    if not is_for_friend:
        reply_markup = contact_client_button(
            user_id=call.from_user.id,
            username=call.from_user.username
        )

    await call.bot.send_message(
        group_id,
        text=group_text,
        reply_markup=reply_markup,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    await state.clear()
    await call.answer()