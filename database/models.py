from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# Async database engine
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(BigInteger)
    api_id: Mapped[int]  = mapped_column(BigInteger)
    full_name: Mapped[str] = mapped_column(String(250))
    phone_number: Mapped[str] = mapped_column(String(13))
    is_admin: Mapped[bool] = mapped_column(default=False)


class New(Base):
    __tablename__ = 'news'

    content_type: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    file_id: Mapped[str] = mapped_column(String, nullable=True)
    caption: Mapped[str] = mapped_column(String)
    caption_entities: Mapped[list] = mapped_column(JSON, nullable=True)


class Promotion(Base):
    __tablename__ = 'promotions'

    content_type: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    file_id: Mapped[str] = mapped_column(String, nullable=True)
    caption: Mapped[str] = mapped_column(String)
    caption_entities: Mapped[list] = mapped_column(JSON, nullable=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
