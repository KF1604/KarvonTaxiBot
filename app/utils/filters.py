from aiogram.filters import BaseFilter
from aiogram.types import Message


class TextOnlyWithWarning(BaseFilter):
    def __init__(self, warning_text: str = None):
        self.warning_text = warning_text or (
            "⚠️ Faqat matnli xabar yuborishingiz mumkin\n\n"
            "❌Iltimos, rasm, video, stiker yoki boshqa fayl yubormang"
        )

    async def __call__(self, message: Message) -> bool:
        if message.text and not any([
            message.photo, message.video, message.audio, message.document,
            message.sticker, message.voice, message.video_note,
            message.animation, message.contact, message.location
        ]):
            return True

        await message.answer(self.warning_text)
        return False
