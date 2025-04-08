from more_itertools.more import with_iter
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm.sync import update

from models import User, db_helper, Organisation
from sqlalchemy.orm import selectinload
# import asyncio


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

async def get_org_by_tg_id(tg_id: int) -> Organisation | None:
    async with db_helper.session_factory() as conn:
        stmt = select(Organisation).join(User, User.organisation_id == Organisation.id).where(User.tg_id == tg_id)
        result = await conn.execute(stmt)
        if result:
            return result.scalar()
        return None

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

async def user_set_org(user: User):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(User)
            .values(organisation_id = user.organisation.id, is_admin=user.is_admin)
            .filter_by(id=user.id)
        )
        print(stmt)
        await conn.execute(stmt)
        await conn.commit()

async def org_set_token(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_token = org.vk_token)
            .filter_by(id=org.id)
        )
        print(stmt)
        await conn.execute(stmt)
        await conn.commit()

async def org_set_vk_group_id(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_group_id = org.vk_group_id)
            .filter_by(id=org.id)
        )
        print(stmt)
        await conn.execute(stmt)
        await conn.commit()


async def set_yd_all(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(yd_login = org.vk_group_id, yd_pass  = org.yd_pass, yd_station_id = org.yd_station_id,
                    yd_groups_ids = org.yd_groups_ids)
            .filter_by(id=org.id)
        )
        print(stmt)
        await conn.execute(stmt)
        await conn.commit()

async def set_organisation_yd_str(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(last_yd_str = org.last_yd_str)
            .filter_by(id=org.id)
        )
        print(stmt)
        await conn.execute(stmt)
        await conn.commit()

# async def update_user(user: User):

# async def get_user_org(tg_id: int) -> Organisation:
#     async with db_helper.session_factory() as conn:
#         stmt = select(Organisation).options(selectinload(User.tg_id))

# async def main():
#     user: User = await get_user(tg_id=154276194)
#     org: Organisation = await get_organisation_by_name(name='Test')
#     user.organisation_id = org.id
#     print(user.organisation_id)
#
# asyncio.run(main())
#
# async def main():
#     org = await get_org_by_tg_id(154276194)
#     # for user in org.users:
#     #     print(user)
#     print(org.id, org.name)
# #
# asyncio.run(main())