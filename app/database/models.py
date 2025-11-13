from sqlalchemy import (
    Integer, String
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, Boolean, TIMESTAMP, ForeignKey, ARRAY
from datetime import datetime
from app.lib.time import now_tashkent

# ─── Bazaviy model ────────────────────────────────
class Base(DeclarativeBase):
    pass

# ─── Foydalanuvchi modeli ─────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_fullname: Mapped[str] = mapped_column(Text, nullable=False)
    username: Mapped[str | None] = mapped_column(Text)
    phone_number: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String, nullable=False, default="user")
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_tashkent,
        nullable=False
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete"
    )

# ─── Buyurtma modeli ──────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))

    user_fullname: Mapped[str] = mapped_column(Text, nullable=False)
    order_type: Mapped[str] = mapped_column(Text, nullable=False)
    from_viloyat: Mapped[str] = mapped_column(Text, nullable=False)
    from_district: Mapped[str] = mapped_column(Text, nullable=False)
    to_viloyat: Mapped[str] = mapped_column(Text, nullable=False)
    to_district: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    comment_to_driver: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_tashkent,
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="orders")

# ─── Feedback modeli ───────────────────────────────
class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_fullname: Mapped[str] = mapped_column(Text, nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)

    answer_text: Mapped[str | None] = mapped_column(Text)
    answered_by: Mapped[int | None] = mapped_column(BigInteger)
    is_answered: Mapped[bool] = mapped_column(Boolean, server_default="false")

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_tashkent,
    )
    answered_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(type_=BigInteger, primary_key=True)
    fullname: Mapped[str] = mapped_column(type_=Text, nullable=False)
    username: Mapped[str | None] = mapped_column(type_=Text, nullable=True)
    phone_number: Mapped[str] = mapped_column(type_=Text, nullable=False)
    car_model: Mapped[str | None] = mapped_column(type_=Text, nullable=True)
    car_number: Mapped[str | None] = mapped_column(type_=Text, nullable=True)
    group_chat_ids: Mapped[list[int]] = mapped_column(type_=ARRAY(BigInteger), default=[])
    is_paid: Mapped[bool] = mapped_column(type_=Boolean, default=False)

    added_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    joined_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        default=now_tashkent,
        nullable=False
    )

    paid_until: Mapped[datetime | None] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        nullable=True
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="driver",
        cascade="all, delete-orphan"
    )

class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    from_vil: Mapped[str] = mapped_column(String(50), nullable=False)
    to_vil: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_tashkent,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    provider: Mapped[str] = mapped_column(String(length=20), nullable=True)
    payment_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)  # "success", "pending", "failed"
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=now_tashkent
    )

    driver: Mapped["Driver"] = relationship(back_populates="payments")