from database.models import async_session
from database.models import User, Promotion, New
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Promotions section
async def set_promo(query):
    async with async_session() as session:
        session.add(query)
        await session.commit()


async def get_promo_list():
    async with async_session() as session:
        result = await session.execute(select(Promotion))
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