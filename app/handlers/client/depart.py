# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
# from aiogram.fsm.context import FSMContext
#
# from app.keyboards.depart_inline import (
#     viloyat_buttons, tuman_buttons,
#     confirm_keyboard, to_main_menu_inline,
#     contact_client_button
# )
# from app.keyboards.depart_reply import phone_keyboard, location_keyboard, comment_keyboard
# from app.data.viloyatlar import VILOYATLAR
# from app.states.depart_states import OrderState
# from app.database.queries import save_order
# from app.utils.get_group import get_group_id
# from app.utils import normalize_phone
# from app.utils.filters import TextOnlyWithWarning
# from app.utils.rate_limiter import is_allowed_to_order
#
# depart_router = Router(name="depart")
#
# @depart_router.callback_query(F.data == "order_depart")
# async def start_depart_callback(call: CallbackQuery, state: FSMContext):
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
#     await state.set_state(OrderState.choose_from_viloyat)
#     await call.message.edit_text(
#         "<b>🚖 Qaysi viloyatdan jo‘nab ketmoqchisiz?</b>",
#         reply_markup=viloyat_buttons(list(VILOYATLAR.keys()))
#     )
#     await call.answer()
#
# @depart_router.callback_query(OrderState.choose_from_viloyat, F.data.startswith("viloyat_"))
# async def from_viloyat(call: CallbackQuery, state: FSMContext):
#     vil = call.data.removeprefix("viloyat_")
#     await state.update_data(from_viloyat=vil)
#
#     await call.message.edit_text(
#         f"<b>🚖 {vil}ning qaysi tumanidan jo‘nab ketayapsiz?</b>",
#         reply_markup=tuman_buttons(VILOYATLAR[vil]),
#         parse_mode="HTML"
#     )
#     await state.set_state(OrderState.choose_from_tuman)
#     await call.answer()
#
# @depart_router.callback_query(OrderState.choose_from_tuman, F.data.startswith("tuman_"))
# async def from_tuman(call: CallbackQuery, state: FSMContext):
#     await state.update_data(from_tuman=call.data.removeprefix("tuman_"))
#     fv = (await state.get_data()).get("from_viloyat")
#     vil_list = [v for v in VILOYATLAR if v != fv]
#     await call.message.edit_text(
#         "<b>🚖 Qaysi viloyatga jo‘nab ketmoqchisiz?</b>",
#         reply_markup=viloyat_buttons(vil_list),
#     )
#     await state.set_state(OrderState.choose_to_viloyat)
#     await call.answer()
#
# @depart_router.callback_query(OrderState.choose_to_viloyat, F.data.startswith("viloyat_"))
# async def to_viloyat(call: CallbackQuery, state: FSMContext):
#     vil = call.data.removeprefix("viloyat_")
#     await state.update_data(to_viloyat=vil)
#
#     await call.message.edit_text(
#         f"<b>🚖 {vil}ning qaysi tumaniga bormoqchisiz?</b>",
#         reply_markup=tuman_buttons(VILOYATLAR[vil]),
#         parse_mode="HTML"
#     )
#     await state.set_state(OrderState.choose_to_tuman)
#     await call.answer()
#
# @depart_router.callback_query(OrderState.choose_to_tuman, F.data.startswith("tuman_"))
# async def to_tuman(call: CallbackQuery, state: FSMContext):
#     tuman = call.data.split("_", 1)[1]
#     await state.update_data(to_tuman=tuman)
#     await state.set_state(OrderState.choose_time)
#     await call.message.edit_text(
#         "<b>🕒 Jo'nab ketish vaqtini kiriting</b>\n\n"
#         "<b>Misol uchun</b>: <code>Ertaga soat 9:00 da</code>",
#         parse_mode="HTML"
#     )
#     await call.answer()
#
# # 5. Vaqt kiritish (faqat qo‘lda yozilgan matn)
# @depart_router.message(OrderState.choose_time, TextOnlyWithWarning())
# async def input_time(message: Message, state: FSMContext):
#     await state.update_data(depart_time=message.text.strip())
#     await state.set_state(OrderState.choose_phone)
#     await message.answer("📞 Telefon raqamingizni yuboring", reply_markup=phone_keyboard())
#
# # 6. Telefon raqamni tekshirish
# @depart_router.message(OrderState.choose_phone)
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
#     await state.set_state(OrderState.choose_location)
#     await message.answer("📍 Geo‑joylashuvingizni yuboring", reply_markup=location_keyboard())
#
# @depart_router.message(OrderState.choose_location)
# async def input_location(message: Message, state: FSMContext):
#     if not message.location:
#         await message.answer("⚠️ Faqat quyidagi tugmalardan foydalaning!")
#         return
#     lat, lon = message.location.latitude, message.location.longitude
#     geo_link = f"https://maps.google.com/?q={lat},{lon}"
#     await state.update_data(location_link=geo_link)
#     await state.set_state(OrderState.choose_comment)
#     await message.answer(
#         "<b>💬 Haydovchiga izoh qoldiring</b>\n\n"
#         "Quyidagi ma’lumotlarni imkon qadar aniq yozing. Bu sizga mos haydovchi topilishiga yordam beradi.\n\n"
#         "<b>Misollar:</b>\n"
#         "• <code>Oldi o‘rindiqda o‘tiraman</code>\n"
#         "• <code>Ayolman, ayol yo‘lovchi bo‘lishi kerak</code>\n"
#         "• <code>2 kishi, 3 ta sumka</code>\n"
#         "• <code>1 kishi, nogironlik aravachasi bor</code>\n"
#         "• <code>1 kishi, 1 ta velosiped, 'rack' kerak</code>\n"
#         "• <code>Ona va 2 bola, 2 ta sumka</code>\n\n"
#         "Iltimos, faqat kerakli ma’lumotlarni yozing 👇",
#         reply_markup=comment_keyboard()
#     )
#
# @depart_router.message(OrderState.choose_comment, TextOnlyWithWarning())
# async def input_comment(message: Message, state: FSMContext):
#     comment = None if message.text == "⏭️ O‘tkazib yuborish" else message.text.strip()
#     await state.update_data(comment=comment)
#     await state.set_state(OrderState.confirm)
#
#     d = await state.get_data()
#     confirm_text = (
#         "<b>⚠️Buyurtmangizni tasdiqlang:</b>\n\n"
#         "<b>Buyurtma turi:</b> 🚖 Jo‘nab ketish\n"
#         f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
#         f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
#         f"<b>🕒 Vaqti:</b> {d.get('depart_time') or 'kiritilmagan'}\n"
#         f"<b>📞 Telefon raqamingiz:</b> {d.get('phone_number') or 'kiritilmagan'}\n"
#         f"<b>📍 Geo-joylashuvingiz:</b> {d['location_link']}\n\n"
#         f"<b>💬 Haydovchiga izoh:</b> {d.get('comment') or 'yo‘q'}"
#     )
#
#     await message.answer("✅ Ma'lumotlar qabul qilindi!", reply_markup=ReplyKeyboardRemove())
#     await message.answer(confirm_text, reply_markup=confirm_keyboard(), parse_mode="HTML", disable_web_page_preview=True)
#
# @depart_router.callback_query(OrderState.confirm, F.data == "confirm_order")
# async def step_confirm(call: CallbackQuery, state: FSMContext):
#     d = await state.get_data()
#
#     await save_order(
#         user_fullname=call.from_user.full_name,
#         user_id=call.from_user.id,
#         order_type="jo'nab ketish",
#         from_viloyat=d["from_viloyat"],
#         from_district=d["from_tuman"],
#         to_viloyat=d["to_viloyat"],
#         to_district=d["to_tuman"],
#         time=d["depart_time"],
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
#             "<b>Buyurtma turi:</b> 🚖 Jo‘nab ketish\n"
#             f"<b>👤 Mijoz:</b> {call.from_user.full_name}\n"
#             f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
#             f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
#             f"<b>🕒 Vaqti:</b> {d.get('depart_time') or  'kiritilmagan'}\n"
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
#     await state.clear()
#     await call.answer()



from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from app.keyboards.depart_inline import (
    viloyat_buttons, tuman_buttons,
    confirm_keyboard, to_main_menu_inline,
    contact_client_button, order_for_whom_buttons
)
from app.keyboards.depart_reply import phone_keyboard, location_keyboard, comment_keyboard
from app.data.viloyatlar import VILOYATLAR
from app.states.depart_states import OrderState
from app.database.queries import save_order, get_user_phone
from app.utils.get_group import get_group_id
from app.utils import normalize_phone
from app.utils.filters import TextOnlyWithWarning
from app.utils.rate_limiter import is_allowed_to_order

depart_router = Router(name="depart")

# --- 1. Buyurtma boshlash ---
@depart_router.callback_query(F.data == "order_depart")
async def start_depart_callback(call: CallbackQuery, state: FSMContext):
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
    await state.set_state(OrderState.choose_for_whom)
    await call.message.edit_text(
        "<b>🚖 Jo'nab ketish bo'limi</b>\n\nUshbu buyurtma kim uchun?",
        reply_markup=order_for_whom_buttons()
    )
    await call.answer()

# --- 2. "O‘zim uchun" yoki "Tanishim uchun" tanlash ---
@depart_router.callback_query(OrderState.choose_for_whom)
async def choose_for_whom(call: CallbackQuery, state: FSMContext):
    choice = "self" if call.data == "order_for_me" else "friend"
    await state.update_data(for_whom=choice)

    await call.message.edit_text(
        "<b>🚖 Qaysi viloyatdan jo‘nab ketiladi?</b>",
        reply_markup=viloyat_buttons(list(VILOYATLAR.keys()))
    )
    await state.set_state(OrderState.choose_from_viloyat)
    await call.answer()

# --- 3. Qayerdan viloyat ---
@depart_router.callback_query(OrderState.choose_from_viloyat, F.data.startswith("viloyat_"))
async def from_viloyat(call: CallbackQuery, state: FSMContext):
    vil = call.data.removeprefix("viloyat_",)
    await state.update_data(from_viloyat=vil)

    await call.message.edit_text(
        f"<b>🚖 {vil}ning qaysi tumanidan jo‘nab ketiladi?</b>",
        reply_markup=tuman_buttons(VILOYATLAR[vil]),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.choose_from_tuman)
    await call.answer()

# --- 4. Qayerdan tuman ---
@depart_router.callback_query(OrderState.choose_from_tuman, F.data.startswith("tuman_"))
async def from_tuman(call: CallbackQuery, state: FSMContext):
    fv = (await state.get_data()).get("from_viloyat")
    await state.update_data(from_tuman=call.data.split("_", 1)[1])

    vil_list = [v for v in VILOYATLAR if v != fv]
    await call.message.edit_text(
        "<b>🚖 Qaysi viloyatga jo‘nab ketiladi?</b>",
        reply_markup=viloyat_buttons(vil_list)
    )
    await state.set_state(OrderState.choose_to_viloyat)
    await call.answer()

# --- 5. Qayerga viloyat ---
@depart_router.callback_query(OrderState.choose_to_viloyat, F.data.startswith("viloyat_"))
async def to_viloyat(call: CallbackQuery, state: FSMContext):
    vil = call.data.removeprefix("viloyat_")
    await state.update_data(to_viloyat=vil)

    await call.message.edit_text(
        f"<b>🚖 {vil}ning qaysi tumaniga boriladi?</b>",
        reply_markup=tuman_buttons(VILOYATLAR[vil])
    )
    await state.set_state(OrderState.choose_to_tuman)
    await call.answer()

# --- 6. Qayerga tuman ---
@depart_router.callback_query(OrderState.choose_to_tuman, F.data.startswith("tuman_"))
async def to_tuman(call: CallbackQuery, state: FSMContext):
    await state.update_data(to_tuman=call.data.split("_", 1)[1])
    await state.set_state(OrderState.choose_time)
    await call.message.edit_text(
        "<b>🕒 Jo'nab ketish vaqtini kiriting</b>\n\n"
        "<b>Misol uchun:</b> <code>Ertaga soat 9:00 da</code>"
    )
    await call.answer()

# --- 7. Vaqt ---
@depart_router.message(OrderState.choose_time, TextOnlyWithWarning())
async def input_time(message: Message, state: FSMContext):
    await state.update_data(depart_time=message.text.strip())
    data = await state.get_data()

    if data.get("for_whom") == "friend":
        await state.set_state(OrderState.choose_phone)
        return await message.answer("📞 Tanishingizning telefon raqamini yuboring", reply_markup=phone_keyboard())

    phone = await get_user_phone(message.from_user.id)
    await state.update_data(phone_number=phone)
    if phone:
        await state.set_state(OrderState.choose_location)
        return await message.answer("📍 Geo-joylashuvingizni yuboring", reply_markup=location_keyboard())

    await state.set_state(OrderState.choose_phone)
    await message.answer("📞 Telefon raqamingizni yuboring", reply_markup=phone_keyboard())

# --- 8. Telefon ---
@depart_router.message(OrderState.choose_phone)
async def input_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    raw_phone = (
        message.contact.phone_number if message.contact else
        message.text.strip() if message.text else None
    )
    phone = normalize_phone(raw_phone) if raw_phone else None

    if not phone:
        return await message.answer(
            "<b>❌ Telefon raqam formati noto‘g‘ri</b>\n\n"
            "<i>⚠️ Faqat O‘zbekiston mobil raqamlari qabul qilinadi</i>",
            reply_markup=phone_keyboard()
        )

    if data.get("for_whom") == "friend":
        user_phone = await get_user_phone(message.from_user.id)
        if user_phone and normalize_phone(user_phone) == phone:
            return await message.answer(
                "<b>⚠️ Ushbu raqam sizga tegishli</b>\n\n"
                "Iltimos, tanishingizga tegishli raqamni kiriting",
                reply_markup=phone_keyboard()
            )

    await state.update_data(phone_number=phone)
    await state.set_state(OrderState.choose_location)
    await message.answer(
        "📍 Tanishingizning geo-joylashuvini yuboring" if data.get("for_whom") == "friend" else "📍 Geo-joylashuvingizni yuboring",
        reply_markup=location_keyboard()
    )

# --- 9. Geo ---
@depart_router.message(OrderState.choose_location)
async def input_location(message: Message, state: FSMContext):
    if not message.location:
        return await message.answer("⚠️ Iltimos, faqat tugmadan foydalaning!")
    lat, lon = message.location.latitude, message.location.longitude
    await state.update_data(location_link=f"https://maps.google.com/?q={lat},{lon}")
    await state.set_state(OrderState.choose_comment)
    await message.answer(
        "<b>💬 Haydovchiga izoh qoldiring</b>\n\n"
        "Quyidagi ma’lumotlarni imkon qadar aniq yozing. Bu sizga mos haydovchi topilishiga yordam beradi.\n\n"
        "<b>Misollar:</b>\n"
        "• <code>Oldi o‘rindiqda o‘tiraman</code>\n"
        "• <code>Ayolman, ayol yo‘lovchi bo‘lishi kerak</code>\n"
        "• <code>2 kishi, 3 ta sumka</code>\n"
        "• <code>1 kishi, nogironlik aravachasi bor</code>\n"
        "• <code>1 kishi, 1 ta velosiped, 'rack' kerak</code>\n"
        "• <code>Ona va 2 bola, 2 ta sumka</code>\n\n"
        "Iltimos, faqat kerakli ma’lumotlarni yozing 👇",
        reply_markup=comment_keyboard()
    )
# --- 10. Izoh ---
@depart_router.message(OrderState.choose_comment, TextOnlyWithWarning())
async def input_comment(message: Message, state: FSMContext):
    comment = None if message.text == "⏭️ O‘tkazib yuborish" else message.text.strip()
    await state.update_data(comment=comment)
    d = await state.get_data()

    await state.set_state(OrderState.confirm)
    phone_text = d.get("phone_number") or "kiritilmagan"
    client_label = "📞 Tanishingizning raqami" if d.get("for_whom") == "friend" else "📞 Telefon raqamingiz"

    confirm_text = (
        "<b>⚠️ Buyurtmangizni tasdiqlang:</b>\n\n"
        "<b>Buyurtma turi:</b> 🚖 Jo‘nab ketish\n"
        f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
        f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
        f"<b>{client_label}:</b> {phone_text}\n"
        f"<b>🕒 Vaqti:</b> {d.get('depart_time') or 'kiritilmagan'}\n"
        f"<b>📍 Geo-joylashuv:</b> {d['location_link']}\n\n"
        f"<b>💬 Haydovchiga izoh:</b> {d.get('comment') or 'yo‘q'}"
    )

    await message.answer("✅ Ma'lumotlar qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    await message.answer(confirm_text, reply_markup=confirm_keyboard(), disable_web_page_preview=True)

# --- 11. Tasdiqlash ---
@depart_router.callback_query(OrderState.confirm, F.data == "confirm_order")
async def step_confirm(call: CallbackQuery, state: FSMContext):
    d = await state.get_data()

    await save_order(
        user_fullname=call.from_user.full_name,
        user_id=call.from_user.id,
        order_type="jo'nab ketish",
        from_viloyat=d["from_viloyat"],
        from_district=d["from_tuman"],
        to_viloyat=d["to_viloyat"],
        to_district=d["to_tuman"],
        time=d["depart_time"],
        phone=d.get("phone_number"),
        location=d["location_link"],
        comment_to_driver=d.get("comment"),
    )

    await call.message.edit_text(
         "<b>✅ Buyurtmangiz qabul qilindi!</b>\n\n"
        "Haydovchilarimiz tez orada siz bilan bog‘lanishadi!\n\n"
        "Bizning xizmatimizdan foydalanganingiz uchun tashakkur!",
        reply_markup=to_main_menu_inline()
    )

    group_id = await get_group_id(d["from_viloyat"], d["to_viloyat"])
    phone_text = d.get("phone_number") or "kiritilmagan"

    group_text = (
        "<b>💥 Yangi buyurtma!</b>\n\n"
        "<b>Buyurtma turi:</b> 🚖 Jo‘nab ketish\n"
        f"<b>👤 Mijoz:</b> {call.from_user.full_name}\n"
        f"<b>🅰️ Qayerdan:</b> {d['from_viloyat']}, {d['from_tuman']}dan\n"
        f"<b>🅱️ Qayerga:</b> {d['to_viloyat']}, {d['to_tuman']}ga\n"
        f"<b>🕒 Vaqti:</b> {d.get('depart_time') or 'kiritilmagan'}\n"
        f"<b>📞 {'Tanishining raqami' if d.get('for_whom') == 'friend' else 'Mijoz raqami'}:</b> {phone_text}\n"
        f"<b>📍 Geo-joylashuvi:</b> {d['location_link']}\n\n"
        f"<b>💬 Izoh:</b> <i>{d.get('comment') or 'yo‘q'}</i>"
    )

    reply_markup = None if d.get("for_whom") == "friend" else contact_client_button(
        user_id=call.from_user.id,
        username=call.from_user.username
    )

    await call.bot.send_message(
        group_id,
        text=group_text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
 
    await state.clear()
    await call.answer()