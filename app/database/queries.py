from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User, Order, Feedback, Driver, Announcement
from app.lib.time import now_tashkent
from sqlalchemy import update
from sqlalchemy import select
from app.database.session import async_session
from app.database.models import Setting

# ─── ID bo‘yicha foydalanuvchi olish ───────────────────
async def get_user_by_id(user_id: int) -> User | None:
    async with async_session() as session:
        return await session.get(User, user_id)

async def get_driver_by_id1(id: int) -> Driver | None:
    async with async_session() as session:
        return await session.get(Driver, id)

# ─── Admin foydalanuvchilar ro‘yxati ────────────────────
async def get_admin_users() -> list[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role.in_(["owner", "super_admin", "admin"]))
        )
        return result.scalars().all()

# ─── Foydalanuvchini bazaga saqlash ─────────────────────
async def save_user(
    user_id: int,
    user_fullname: str,
    phone_number: str | None = None,
    username: str = "",
) -> None:
    async with async_session() as session:
        if not await session.get(User, user_id):
            user = User(
                id=user_id,
                user_fullname=user_fullname,
                phone_number=phone_number,
                username=username,
                joined_at=now_tashkent()
            )
            session.add(user)
            await session.commit()

# ─── Buyurtmani bazaga yozish ──────────────────────────
async def save_order(
    user_id: int,
    user_fullname: str,
    order_type: str,
    from_viloyat: str,
    from_district: str,
    to_viloyat: str,
    to_district: str,
    time: str,
    phone: str | None,
    location: str,
    comment_to_driver: str | None,
) -> int:
    async with async_session() as session:
        order = Order(
            user_id=user_id,
            user_fullname=user_fullname,
            order_type=order_type,
            from_viloyat=from_viloyat,
            from_district=from_district,
            to_viloyat=to_viloyat,
            to_district=to_district,
            time=time,
            phone=phone,
            location=location,
            comment_to_driver=comment_to_driver,
            created_at=now_tashkent()
        )
        session.add(order)
        await session.commit()
        return order.order_id

# ─── Fikr-mulohazani bazaga yozish ─────────────────────
async def save_feedback(user_id: int, fullname: str, text: str) -> Feedback:
    async with async_session() as session:
        fb = Feedback(
            user_id=user_id,
            user_fullname=fullname,
            message_text=text
        )
        session.add(fb)
        await session.commit()
        await session.refresh(fb)
        return fb

async def get_driver_by_id(session: AsyncSession, user_id: int) -> Driver | None:
    result = await session.execute(
        select(Driver).where(Driver.id == user_id)
    )
    return result.scalar_one_or_none()

async def is_driver(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(select(Driver.id).where(Driver.id == user_id))
    return result.scalar_one_or_none() is not None

async def update_driver_phone(user_id: int, new_phone: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(Driver).where(Driver.id == user_id))
        driver = result.scalar_one_or_none()
        if driver:
            driver.phone_number = new_phone
            await session.commit()

async def update_user_phone(user_id: int, phone: str):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(phone_number=phone)
        )
        await session.commit()

#----Bot rejimiga oid querylar------
async def get_unpaid_drivers():
    async with async_session() as session:
        result = await session.execute(
            select(Driver).where(Driver.is_paid == False)
        )
        return result.scalars().all()

# ─── Bot rejimini olish ─────────────────────
async def get_bot_mode() -> str:
    async with async_session() as session:
        result = await session.get(Setting, "bot_mode")
        return result.value if result else "free"  # default holat: 'free'

# ─── Bot rejimini o‘zgartirish va boshlanish vaqtini belgilash ────────
async def set_bot_mode(mode: str) -> None:
    async with async_session() as session:
        # 1. Bot rejimini yangilash
        bot_mode_setting = await session.get(Setting, "bot_mode")
        if bot_mode_setting:
            bot_mode_setting.value = mode
        else:
            session.add(Setting(key="bot_mode", value=mode))

        # 2. Pullik rejimga o‘tilsa, boshlanish vaqtini saqlash
        if mode == "paid":
            now = now_tashkent()
            now_str = now.isoformat()

            paid_started_setting = await session.get(Setting, "paid_mode_started_at")
            if paid_started_setting:
                paid_started_setting.value = now_str
            else:
                session.add(Setting(key="paid_mode_started_at", value=now_str))

            # 3. Eski haydovchilarga 3 kunlik trial (faqat bir marta)
            deadline = now + timedelta(days=3)
            await session.execute(
                update(Driver)
                .where(Driver.paid_until == None)
                .values(paid_until=deadline)
            )

        await session.commit()

async def get_setting_value(session, key: str) -> str | None:
    result = await session.execute(
        select(Setting.value).where(Setting.key == key)
    )
    return result.scalar_one_or_none()

async def get_user_phone(user_id: int) -> str | None:
    async with async_session() as session:
        stmt = select(User.phone_number).where(User.id == user_id)
        result = await session.execute(stmt)
        phone = result.scalar_one_or_none()
        return phone

async def get_active_announcement(driver_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Announcement).where(
                Announcement.driver_id == driver_id,
                Announcement.is_active.is_(True)
            )
        )
        return result.scalar_one_or_none()

# Faol e'lonni olish
async def get_active_announcement_by_driver(driver_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Announcement).where(
                Announcement.driver_id == driver_id,
                Announcement.is_active == True
            )
        )
        return result.scalar_one_or_none()

# E'lonni deaktivatsiya qilish
async def deactivate_announcement(announcement_id: int):
    async with async_session() as session:
        await session.execute(
            update(Announcement)
            .where(Announcement.id == announcement_id)
            .values(is_active=False)
        )
        await session.commit()