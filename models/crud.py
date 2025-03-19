from more_itertools.more import with_iter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, db_helper
import asyncio


async def create_user( tg_id: str) -> User:
    async with db_helper.session_factory() as conn:
        user = User(tg_id=tg_id)
        conn.add(user)
        await conn.commit()
        print(user)
        return user

asyncio.run(create_user('asdasda'))

