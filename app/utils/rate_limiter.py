from datetime import timedelta
from sqlalchemy import select, desc
from app.database.session import async_session
from app.database.models import Order
from app.lib.time import now_tashkent

LIMIT_MINUTES = 5

async def is_allowed_to_order(user_id: int) -> tuple[bool, str | None]:
    # check_from endi Toshkent bo‘yicha
    check_from = now_tashkent() - timedelta(minutes=LIMIT_MINUTES)

    async with async_session() as session:
        result = await session.execute(
            select(Order.created_at)
            .where(Order.user_id == user_id)
            .where(Order.created_at >= check_from)
            .order_by(desc(Order.created_at))
            .limit(1)
        )
        last_order_time = result.scalar_one_or_none()

        if last_order_time:
            next_time = (last_order_time + timedelta(minutes=LIMIT_MINUTES)) \
                .strftime("%H:%M")
            return False, next_time

        return True, None