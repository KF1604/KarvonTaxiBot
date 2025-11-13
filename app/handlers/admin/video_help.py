from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router(name="video_helps")

# 🎥 Video file_id lar
CLIENT_VIDEO_ID = "BAACAgIAAxkBAAICwWjEEEu2MGfE3JA5nzQXKH7HFwABPwACSnQAAsOmIEqmmVTu-D8YAzYE"
DRIVER_VIDEO_ID = "BAACAgIAAxkBAAICw2jEEHtHnQ7n-38ticE8hDipJQl_AAJMdAACw6YgSoovFb2Y4WTWNgQ"


# 🎥 Yo‘lovchilar uchun video
@router.callback_query(F.data == "video_client")
async def send_client_video(callback: CallbackQuery):
    await callback.message.answer_video(
        video=CLIENT_VIDEO_ID,
        caption="<b>🎥 Bu yo‘lovchilar uchun videoqo‘llanma\n\n"
                "Botni qayta ishga tushirish uchun /start ni bosing</b>",
        parse_mode="HTML"
    )
    await callback.answer()


# 🎥 Haydovchilar uchun video
@router.callback_query(F.data == "video_driver")
async def send_driver_video(callback: CallbackQuery):
    await callback.message.answer_video(
        video=DRIVER_VIDEO_ID,
        caption="<b>🎥 Bu haydovchilar uchun videoqo‘llanma\n\n"
                "Botni qayta ishga tushirish uchun /start ni bosing</b>",
        parse_mode="HTML"
    )
    await callback.answer()