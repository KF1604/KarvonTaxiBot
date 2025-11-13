from __future__ import annotations
import os
from pathlib import Path
from typing import Final, Dict
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"))

def getenv_or_raise(name: str) -> str:
    val = os.getenv(name)
    if val is None:
        raise RuntimeError(f"❌ M/O‘zgaruvchi yo‘q: {name}  (.env ni tekshiring)")
    return val

# ─── BOT TOKEN ─────────────────────────────────────────────────────────────────
API_TOKEN: Final = getenv_or_raise("API_TOKEN")

CLICK_TOKEN = os.getenv("CLICK_TOKEN")

# Bot rejimini bazadan olish funksiyasi
async def get_bot_mode_async():
    from app.database.queries import get_bot_mode
    return await get_bot_mode()

BOT_MODE = "free"
# ─── DATABASE ──────────────────────────────────────────────────────────────────
DB_NAME:     Final = getenv_or_raise("DB_NAME")
DB_USER:     Final = getenv_or_raise("DB_USER")
DB_PASSWORD: Final = getenv_or_raise("DB_PASSWORD")
DB_HOST:     Final = getenv_or_raise("DB_HOST")
DB_PORT:     Final = getenv_or_raise("DB_PORT")

# ─── CLICK CONFIG ─────────────────────────────────────────────
CLICK_SERVICE_ID: Final = getenv_or_raise("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID: Final = getenv_or_raise("CLICK_MERCHANT_ID")
CLICK_SECRET_KEY: Final = getenv_or_raise("CLICK_SECRET_KEY")
CLICK_MERCHANT_USER_ID: Final = getenv_or_raise("CLICK_MERCHANT_USER_ID")

# ─── GROUP IDS (16 ta) ─────────────────────────────────────────────────────────
_GROUP_ENV_MAP: Dict[str, str] = {
    # Toshkent ↔ Toshkent (shahar↔viloyat yoki o‘zaro)
    "toshkent_toshkent": "GROUP_TOSHKENT_TOSHKENT",

    # Toshkent ↔ Vodiy
    "toshkent_andijon":  "GROUP_TOSHKENTSH_ANDIJON",
    "toshkent_fargona":  "GROUP_TOSHKENTSH_FARGONA",
    "toshkent_namangan": "GROUP_TOSHKENT_NAMANGAN",

    # Toshkent ↔ Voha
    "toshkent_jizzax":        "GROUP_TOSHKENT_JIZZAX",
    "toshkent_qashqadaryo":   "GROUP_TOSHKENTSH_QASHQADARYO",
    "toshkent_sirdaryo":      "GROUP_TOSHKENTSH_SIRDARYO",
    "toshkent_surxondaryo":   "GROUP_TOSHKENTSH_SURXONDARYO",
    "toshkent_navoiy":        "GROUP_TOSHKENTSH_NAVOIY",
    "toshkent_samarqand":     "GROUP_TOSHKENTSH_SAMARQAND",
    "toshkent_buxoro":        "GROUP_TOSHKENTSH_BUXORO",
    "toshkent_xorazm":        "GROUP_TOSHKENTSH_XORAZM",
    "toshkent_qoraqalpogiston": "GROUP_TOSHKENTSH_QORAQALPOGISTON",

    # Hudud ↔ Hudud (Toshkentsiz)
    "vodiy_vodiy": "GROUP_VODIY_VODIY",
    "voha_voha":   "GROUP_VOHA_VOHA",
    "vodiy_voha":  "GROUP_VODIY_VOHA",
}

GROUPS: Final[Dict[str, int]] = {
    k: int(getenv_or_raise(env)) for k, env in _GROUP_ENV_MAP.items()
}

# Haydovchilar uchun alohida guruhlar
_DRIVER_GROUP_MAP: Dict[str, str] = {
    "toshkent_toshkent": "GROUPDRV_TOSHKENT_TOSHKENT",

    # Toshkent ↔ Vodiy
    "toshkent_andijon":  "GROUPDRV_TOSHKENT_ANDIJON",
    "toshkent_fargona":  "GROUPDRV_TOSHKENT_FARGONA",
    "toshkent_namangan": "GROUPDRV_TOSHKENT_NAMANGAN",

    # Toshkent ↔ Voha
    "toshkent_jizzax":        "GROUPDRV_TOSHKENT_JIZZAX",
    "toshkent_qashqadaryo":   "GROUPDRV_TOSHKENT_QASHQADARYO",
    "toshkent_sirdaryo":      "GROUPDRV_TOSHKENT_SIRDARYO",
    "toshkent_surxondaryo":   "GROUPDRV_TOSHKENT_SURXONDARYO",
    "toshkent_navoiy":        "GROUPDRV_TOSHKENT_NAVOIY",
    "toshkent_samarqand":     "GROUPDRV_TOSHKENT_SAMARQAND",
    "toshkent_buxoro":        "GROUPDRV_TOSHKENT_BUXORO",
    "toshkent_xorazm":        "GROUPDRV_TOSHKENT_XORAZM",
    "toshkent_qoraqalpogiston": "GROUPDRV_TOSHKENT_QORAQALPOGISTON",

    # Hudud ↔ Hudud (Toshkentsiz)
    "vodiy_vodiy": "GROUPDRV_VODIY_VODIY",
    "voha_voha":   "GROUPDRV_VOHA_VOHA",
    "vodiy_voha":  "GROUPDRV_VODIY_VOHA",
}

GROUPS_DRIVER: Final[Dict[str, int]] = {
    k: int(getenv_or_raise(env)) for k, env in _DRIVER_GROUP_MAP.items()
}

# Har ikkala lug‘atni birlashtirib, umumiy ruxsat berilgan chatlar ro‘yxati
ALLOWED_CHATS: Final[list[int]] = list(GROUPS.values()) + list(GROUPS_DRIVER.values())