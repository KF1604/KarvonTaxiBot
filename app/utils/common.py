from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

async def send_prompt(
    *,
    obj: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | None,
    state: FSMContext,
    parse_mode: str | ParseMode = ParseMode.HTML,
):
    if isinstance(obj, CallbackQuery):
        # Inline tugma yubormoqchi bo‘lsangiz
        if isinstance(reply_markup, InlineKeyboardMarkup) or reply_markup is None:
            await obj.message.edit_text(
                text, reply_markup=reply_markup, parse_mode=parse_mode
            )
        else:
            # Reply tugma bo‘lsa, yangi xabar bilan yuboriladi
            await obj.message.answer(
                text, reply_markup=reply_markup, parse_mode=parse_mode
            )
    else:
        await obj.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)