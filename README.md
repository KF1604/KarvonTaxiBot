<div align="center">

# 🚖 KarvonTaxiBot  
### O‘zbekiston bo‘ylab viloyatlararo taxi buyurtma va e’lon bot

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-1572B6?logo=telegram)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)
![Async](https://img.shields.io/badge/Async-SQLAlchemy%20|%20Aiogram-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 🧩 Loyihaning qisqacha tavsifi

**KarvonTaxizBot** — bu O‘zbekiston bo‘ylab viloyatlararo taxi xizmatini avtomatlashtiruvchi Telegram bot.  
Mijozlar o‘zlari yoki tanishlari uchun buyurtma bera oladi, haydovchilar esa o‘z yo‘nalishlarini e’lon qilib, mijozlarni to‘g‘ridan-to‘g‘ri topishadi.

---

## ⚙️ Asosiy imkoniyatlar

✅ **Buyurtmalar tizimi**
- Mijoz o‘zi yoki tanishi uchun buyurtma bera oladi.
- Har bir viloyat uchun **tumanlar**, **jo‘nash vaqti**, **geojoylashuv**, va **haydovchiga izoh** qo‘shish mumkin.
- Buyurtma tanlangan yo‘nalishga qarab **tegishli haydovchilar guruhiga avtomatik** yuboriladi.
- Har 5 daqiqada faqat **1 ta buyurtma** berish mumkin — bu **takroriy buyurtmalarni oldini oladi**.

💰 **Pullik va bepul rejim**
- Bot `settings` jadvali orqali rejimni o‘zgartiradi.
- Pullik rejimda haydovchilar **Click** orqali obuna to‘lovini amalga oshiradilar.
- Obuna muddati tugashiga **1 kun qolganda ogohlantirish** yuboriladi.
- To‘lov qilmagan haydovchilar **yopiq buyurtma guruhidan** avtomatik chiqariladi.

💬 **Professional feedback tizimi**
- Foydalanuvchi admin javobini olmaguncha yangi xabar yubora olmaydi.
- Bu takroriy va keraksiz murojaatlarni oldini oladi.

📣 **Haydovchi e’lonlari**
- Haydovchi o‘z yo‘nalishida e’lon yaratadi, bot har 5 daqiqada uni yangilab joylaydi.
- Haydovchi **“E’lonni to‘xtatish”** tugmasi orqali e’lonni o‘zi xohlagan vaqtda to‘xtata oladi.

---

## 🧠 Texnologiyalar

| Texnologiya | Tavsif |
|--------------|---------|
| **Python 3.11+** | Asosiy dasturlash tili |
| **Aiogram 3.x** | Telegram Bot Framework |
| **PostgreSQL** | Asosiy ma’lumotlar bazasi |
| **SQLAlchemy (async)** | ORM va asinxron so‘rovlar |
| **Click API** | To‘lov tizimi integratsiyasi |
| **Docker (ixtiyoriy)** | Konteynerlash va deploy uchun |


## 🛠️ O‘rnatish

```bash
git clone https://github.com/username/TaxiUzBot.git
cd TaxiUzBot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## .env faylini yarating

```bash
BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
CLICK_TOKEN=398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065
```

## 🚀 Ishga tushirish
```bash
python main.py
```

------------------------------------------------------------------------------------------------


<div align="center">

# 🚖 KarvonTaxiBot  
### Interregional taxi booking and announcement bot across Uzbekistan

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-1572B6?logo=telegram)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)
![Async](https://img.shields.io/badge/Async-SQLAlchemy%20|%20Aiogram-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 🧩 Project Overview

**KarvonTaxiBot** is a Telegram bot that automates interregional taxi services across Uzbekistan.  
Clients can place orders for themselves or their friends, and drivers can post their routes to find passengers directly.

---

## ⚙️ Key Features

✅ **Order System**
- Clients can create orders for themselves or for others.  
- Each region includes **district selection**, **departure time**, **geo-location**, and **driver notes**.  
- Orders are automatically forwarded to the **relevant driver group** based on the selected route.  
- Users can submit only **one order every 5 minutes** — preventing duplicate requests.

💰 **Free and Paid Modes**
- The bot mode can be switched via the `settings` table.  
- In paid mode, drivers make subscription payments via **Click integration**.  
- Drivers are **notified 1 day before** their subscription expires.  
- Non-paying drivers are **automatically removed** from the private driver order group.

💬 **Professional Feedback System**
- Users can send only one message until the admin responds — avoiding spam or repeated messages.  

📣 **Driver Announcements**
- Drivers can create automatic route posts, which the bot republishes every 5 minutes.  
- Drivers can stop these automatic posts anytime via the **“Stop Announcement”** button.

---

## 🧠 Technologies

| Technology | Description |
|-------------|-------------|
| **Python 3.11+** | Main programming language |
| **Aiogram 3.x** | Telegram Bot Framework |
| **PostgreSQL** | Main database |
| **SQLAlchemy (async)** | ORM and asynchronous query management |
| **Click API** | Integrated payment system |
| **Docker (optional)** | Containerization and deployment |

---

## 🛠️ Installation

```bash
git clone https://github.com/username/KarvonTaxiBot.git
cd KarvonTaxiBot
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
