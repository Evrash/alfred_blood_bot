from more_itertools.more import with_iter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, db_helper, Organisation
from sqlalchemy.orm import selectinload
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

async def get_organisation_by_name(name: str) -> Organisation | None:
    async with db_helper.session_factory() as conn:
        stmt = select(Organisation).where(Organisation.name==name)
        result = await conn.execute(stmt)
        if result:
            return result.scalar()
        return None

async def create_organisation(name: str) -> Organisation:
    async with db_helper.session_factory() as conn:
        org = Organisation(name=name)
        conn.add(org)
        await conn.commit()
        return org

# async def get_user_org(tg_id: int) -> Organisation:
#     async with db_helper.session_factory() as conn:
#         stmt = select(Organisation).options(selectinload(User.tg_id))