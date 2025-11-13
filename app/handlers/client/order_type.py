from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.depart_inline import order_type_buttons
from aiogram.fsm.context import FSMContext
from app.database.queries import is_driver
from app.database.session import async_session

order_type_router = Router(name="order_type")

# @order_type_router.callback_query(F.data == "start_mijoz")
# async def handle_mijoz(callback: CallbackQuery):
#     await callback.message.edit_text(
#         "<b>🙋‍♂️ Mijoz bo‘limi</b>\n\nBuyurtma turini tanlang:",
#         reply_markup=order_type_buttons(),
#         parse_mode="HTML"
#     )

@order_type_router.callback_query(F.data == "start_mijoz")
async def handle_mijoz(callback: CallbackQuery):
    async with async_session() as session:
        if await is_driver(session, callback.from_user.id):
            await callback.answer(
                "⚠️ Siz haydovchi sifatida ro‘yxatdan o‘tgansiz\n\n"
                "Tizimdan yo'lovchi sifatida foydalana olmaysiz",
                show_alert=True
            )
            return

    await callback.message.edit_text(
        "<b>🙋‍♂️ Yo'lovchi bo‘limi</b>\n\nBuyurtma turini tanlang:",
        reply_markup=order_type_buttons(),
        parse_mode="HTML"
    )

@order_type_router.callback_query(F.data == "order_depart")
async def handle_depart(callback: CallbackQuery, state: FSMContext):
    # Bu yerda depart.py dagi FSM boshlanadi
    from app.handlers.client.depart import start_depart_callback
    await start_depart_callback(callback, state)

@order_type_router.callback_query(F.data == "order_parcel")
async def handle_parcel(callback: CallbackQuery, state: FSMContext):
    # Bu yerda parcel.py dagi FSM boshlanadi
    from app.handlers.client.parcel import start_parcel_callback
    await start_parcel_callback(callback, state)