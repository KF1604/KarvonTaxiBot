import re
from contextlib import suppress
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from urllib.parse import urlparse

# def normalize_phone(raw: str) -> str | None:
#     digits = re.sub(r"[^\d]", "", raw)
#
#
#     if len(digits) == 9 and digits.startswith("9"):
#         digits = "998" + digits
#
#     return f"+{digits}" if digits.startswith("998") and len(digits) == 12 else None

VALID_CODES = {"90", "91", "70", "77", "95", "99", "50", "93", "94", "20", "33", "87", "88", "97"}

def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"\D", "", raw)

    if len(digits) == 9 and digits[:2] in VALID_CODES:
        digits = "998" + digits

    elif len(digits) == 9 and digits.startswith("9"):
        digits = "998" + digits

    elif len(digits) == 12 and digits.startswith("998"):
        pass
    else:
        return None

    return f"+{digits}" if digits[3:5] in VALID_CODES else None

async def delete_welcome_message(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("welcome_message_id")
    if msg_id:
        with suppress(Exception):
            await call.bot.delete_message(chat_id=call.message.chat.id, message_id=msg_id)
        await state.update_data(welcome_message_id=None)

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False


UZB_REGIONS = {"01", "10", "20", "25", "30", "40", "50", "60", "70", "75", "80", "85", "90", "95"}

def format_car_number(text: str) -> str | None:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", text).upper()
    if len(cleaned) < 7 or cleaned[:2] not in UZB_REGIONS:
        return None

    prefix, body = cleaned[:2], cleaned[2:]

    if match := re.fullmatch(r"([A-Z])(\d{3})([A-Z]{2})", body):
        return f"{prefix} | {match[1]} {match[2]} {match[3]}"
    if match := re.fullmatch(r"(\d{3})([A-Z]{3})", body):
        return f"{prefix} | {match[1]} {match[2]}"
    return None
