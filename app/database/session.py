from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from app.database.models import Base

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ─── Asinxron engine ───────────────────────────────
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=50,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# ─── Session Factory ───────────────────────────────
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ─── DB ni 1-marta yaratish uchun funksiya ──────────
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
