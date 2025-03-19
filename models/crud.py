from more_itertools.more import with_iter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, db_helper
import asyncio


async def create_user(tg_id: int) -> User:
    async with db_helper.session_factory() as conn:
        user = User(tg_id=tg_id)
        conn.add(user)
        await conn.commit()
        print(user)
        return user

async def get_user(tg_id: int) -> User | None:
    async with db_helper.session_factory() as conn:
        # result = await conn.get(User, tg_id)
        stmt = select(User).where(User.tg_id==tg_id)
        result = await conn.execute(stmt)
        if result:
            return result.scalar()
        return None

async def get_or_create(tg_id: int) -> User:
    result = await get_user(tg_id)
    if not result:
        return await create_user(tg_id)
    return result
