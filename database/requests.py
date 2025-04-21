from database.models import async_session
from database.models import User, Promotion, New
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession


# Users section
async def get_users_list():
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users if users else None


async def get_admin_users_list():
    async with async_session() as session:
        result = await session.execute(select(User).where(User.is_admin == True))
        admins = result.scalars().all()
        return admins if admins else None


async def get_user(chat_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == chat_id))
        return user if user else None


async def create_user(query):
    async with async_session() as session:
        session.add(query)
        await session.commit()


async def is_user_authenticated(chat_id: int) -> bool:
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == chat_id)
        )
        return bool(user)



# Promotions section
async def set_promo(query):
    async with async_session() as session:
        session.add(query)
        await session.commit()


async def get_promo_list():
    async with async_session() as session:
        result = await session.execute(
            select(Promotion).
            order_by(desc(Promotion.created_at))
        )
        promos = result.scalars().all()
        return promos if promos else None


async def get_active_promo_list():
    async with async_session() as session:
        result = await session.execute(
            select(Promotion)
            .where(Promotion.is_active == True)
            .order_by(desc(Promotion.created_at))
        )
        promos = result.scalars().all()
        return promos if promos else None


async def get_promo(promo_id: int):
    async with async_session() as session:
        promo = await session.scalar(select(Promotion).where(Promotion.id == promo_id))
        return promo if promo else None


async def set_promo_activation(promo_id: int, activate: bool):
    async with async_session() as session:
        promo = await session.scalar(select(Promotion).where(Promotion.id == promo_id))

        if promo:
            promo.is_active = activate
            return await session.commit()
        return None


async def update_promo(promo_id: int, query):
    async with async_session() as session:
        promo = await session.scalar(select(Promotion).where(Promotion.id == promo_id))
        if promo:
            promo.content_type = query.content_type
            promo.file_id = query.file_id
            promo.caption = query.caption
            promo.caption_entities = query.caption_entities
            await session.commit()
            return True
        return False


async def delete_promo(promo_id: int):
    async with async_session() as session:
        promo = await session.scalar(select(Promotion).where(Promotion.id == promo_id))
        if promo:
            await session.delete(promo)
            await session.commit()
            return True
        return False


# News section
async def set_new(query):
    async with async_session() as session:
        session.add(query)
        await session.commit()


async def get_new_list():
    async with async_session() as session:
        result = await session.execute(
            select(New)
            .where(New.is_active == True)
            .order_by(desc(New.created_at))
        )
        news = result.scalars().all()
        return news if news else None


async def get_new(new_id: int):
    async with async_session() as session:
        new = await session.scalar(
            select(New)
            .where(New.id == new_id)
            .order_by(desc(New.created_at))
        )
        return new if new else None


async def set_new_activation(new_id: int, activate: bool):
    async with async_session() as session:
        new = await session.scalar(select(New).where(New.id == new_id))

        if new:
            new.is_active = activate
            return await session.commit()
        return None


async def update_new(new_id: int, query):
    async with async_session() as session:
        new = await session.scalar(select(New).where(New.id == new_id))
        if new:
            new.content_type = query.content_type
            new.file_id = query.file_id
            new.caption = query.caption
            new.caption_entities = query.caption_entities
            await session.commit()
            return True
        return False


async def delete_new(new_id: int):
    async with async_session() as session:
        new = await session.scalar(select(New).where(New.id == new_id))
        if new:
            await session.delete(new)
            await session.commit()
            return True
        return False

