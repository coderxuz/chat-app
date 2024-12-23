from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from os import getenv

from common import logger

load_dotenv()

DB_URL = getenv("DATABASE_URL")
if DB_URL:
    engine = create_engine(DB_URL)
else:
    raise ValueError("DB_URL didn't find")

ASYNC_DB_URL = getenv("ASYNC_DATABASE_URL")

if ASYNC_DB_URL:
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
else:
    raise ValueError("DB_URL didn't find")

SessionLocal = sessionmaker(bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.warning(f"Session error \n {e}")
            raise
        finally:
            await session.close()
