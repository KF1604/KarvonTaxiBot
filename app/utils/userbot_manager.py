import os
import asyncio
import logging
from telethon import TelegramClient, events, Button
from telethon.errors import FloodWaitError, RPCError
from dotenv import load_dotenv

# 🔹 .env fayldan o‘qish
load_dotenv()

# 🔑 API ma'lumotlari
API_ID = int(os.getenv("API_ID", 28282608))
API_HASH = os.getenv("API_HASH", "b2f8680bc4637b529ae8745bea5d2831")

# 🔒 Sessiya fayli (bir marta login uchun)
SESSION_NAME = os.getenv("USERBOT_SESSION", "userbot_session")

# 🔧 Logger sozlamalari
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 🧠 Userbot client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# 🗺️ Viloyatlar bo‘yicha manba va maqsad guruhlar
VILOYATLAR_GURUHLAR = {
    "Toshkent": {
        "source": [],
        "target": [-1002528988283],
    },
    "Andijon": {
        "source": [-1001739925049, -1001151713075, -1002663700498],
        "target": [-1002452485366],
    },
    "Farg‘ona": {
        "source": [],
        "target": [-1002658346365],
    },
    "Namangan": {
        "source": [],
        "target": [-1002594856326],
    },
    "Jizzax": {
        "source": [],
        "target": [-1002598292761],
    },
    "Qashqadaryo": {
        "source": [],
        "target": [-1002607298211],
    },
    "Sirdaryo": {
        "source": [],
        "target": [-1002677169749],
    },
    "Surxondaryo": {
        "source": [],
        "target": [-1002604719567],
    },
    "Navoiy": {
        "source": [],
        "target": [-1002513667608],
    },
    "Samarqand": {
        "source": [-1001807864075],
        "target": [-1002600477374],
    },
    "Buxoro": {
        "source": [],
        "target": [-1002579554614],
    },
    "Xorazm": {
        "source": [],
        "target": [-1002674548106],
    },
    "Qoraqalpog'iston": {
        "source": [],
        "target": [-1002676199277],
    }
}

# 🔍 Kalit so‘zlar
TRIGGER_WORDS = [
    "2 ta odam bor", "1 ta odam bor", "taksi kerak", "taxi kerak",
    "moshina kerak", "mowina kerak", "srochni ketish kerak", "ketish kerak"
]


@client.on(events.NewMessage)
async def handle_new_message(event):
    """Begona guruhdagi e’lonlarni kuzatib, tegishli guruhga yuborish."""
    chat_id = event.chat_id
    sender = await event.get_sender()
    message_text = (event.message.message or "").strip().lower()

    if not any(word in message_text for word in TRIGGER_WORDS):
        return

    # 👤 Foydalanuvchi ma'lumotlari
    full_name = (sender.first_name or "") + (f" {sender.last_name}" if sender.last_name else "")
    username = f"@{sender.username}" if sender.username else "Yopiq akkaunt"
    user_id = sender.id

    # 📋 Formatlangan xabar
    caption = (
        "<b>🆕 Yangi buyurtma!</b>\n\n"
        f"👤 <b>Ismi:</b> {full_name}\n"
        f"🔗 <b>Akkaunt:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        f"💬 <b>Mijoz xabari:</b>\n{event.message.message}"
    )

    # 💬 Tugma (akkaunt ochiq/yopiq)
    if sender.username:
        buttons = [[Button.url("💬 Mijozga yozish", f"https://t.me/{sender.username}")]]
    else:
        buttons = [[Button.inline("💬 Mijozga yozish", data=f"private_alert_{user_id}")]]

    # 🔄 Viloyatlar bo‘yicha yuborish
    for viloyat, guruhlar in VILOYATLAR_GURUHLAR.items():
        if chat_id in guruhlar["source"]:
            for target_id in guruhlar["target"]:
                try:
                    await client.send_message(
                        target_id,
                        caption,
                        buttons=buttons,
                        parse_mode="html"
                    )
                    logger.info(f"✅ [{viloyat}] Buyurtma yuborildi → {target_id}")

                except FloodWaitError as fw:
                    logger.warning(f"⏳ FloodWait: {fw.seconds}s ({viloyat})")
                    await asyncio.sleep(fw.seconds)
                    await client.send_message(target_id, caption, buttons=buttons, parse_mode="html")

                except RPCError as rpc_err:
                    logger.error(f"⚠️ RPC xato [{viloyat} → {target_id}]: {rpc_err}")

                except Exception as e:
                    logger.error(f"🚨 Noma’lum xato [{viloyat} → {target_id}]: {e}")
            break


# ⚠️ Yopiq akkaunt uchun alert
@client.on(events.CallbackQuery(pattern=r"^private_alert_"))
async def show_private_alert(event):
    await event.answer("❌ Bu foydalanuvchi akkaunti yopiq, yozib bo‘lmaydi.", alert=True)


# 🚀 Userbotni ishga tushirish
async def start_userbot():
    """Userbotni ishga tushirish (main.py dan chaqiriladi)."""
    try:
        await client.start()
        logger.info("✅ Userbot ishga tushdi va guruhlarni kuzatmoqda...")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"❌ Userbot ishga tushmadi: {e}")