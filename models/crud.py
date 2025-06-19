import datetime

from sqlalchemy import select, update, func, delete

from models import User, db_helper, Organisation, Statistic
from sqlalchemy.orm import selectinload


async def create_user(tg_id: int, full_name: str|None = None, username: str|None = None) -> User:
    async with db_helper.session_factory() as conn:
        user = User(tg_id=tg_id, full_name=full_name, username=username)
        conn.add(user)
        await conn.commit()
        return user

async def update_user(user:User):
    async with db_helper.session_factory() as conn:
        stmt = (
            update(User)
            .values(full_name=user.full_name, username=user.username)
            .filter_by(id=user.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def get_user(tg_id: int) -> User | None:
    async with db_helper.session_factory() as conn:
        # result = await conn.get(User, tg_id)
        stmt = select(User).options(selectinload(User.organisation)).where(User.tg_id==tg_id)
        result = await conn.execute(stmt)
        return result.scalar()

async def get_user_by_id(id: int) -> User | None:
    async with db_helper.session_factory() as conn:
        stmt = select(User).where(User.id == id)
        result = await conn.execute(stmt)
        return result.scalar()

async def get_or_create(tg_id: int, full_name: str|None = None, username: str|None = None) -> User:
    result = await get_user(tg_id)
    if not result:
        return await create_user(tg_id, full_name, username)
    result.full_name, result.username = full_name, username
    await update_user(result)
    return result

async def get_org_by_tg_id(tg_id: int) -> Organisation | None:
    async with db_helper.session_factory() as conn:
        stmt = select(Organisation).join(User, User.organisation_id == Organisation.id).where(User.tg_id == tg_id)
        result = await conn.execute(stmt)
        return result.scalar()

async def get_org_by_id(id: int) -> Organisation | None:
    async with db_helper.session_factory() as conn:
        stmt = select(Organisation).where(Organisation.id == id)
        result = await conn.execute(stmt)
        return result.scalar()
        #     return result.scalar()
        # return None

async def get_org_admins(org_id: int) -> list[User] | None:
    async with db_helper.session_factory() as conn:
        stmt = select(User).where(User.is_admin == True, User.organisation_id == org_id)
        result = await conn.execute(stmt)
        return result.scalars().all()

async def get_org_users(org_id: int) -> list[User] | None:
    async with db_helper.session_factory() as conn:
        stmt = select(User).where(User.organisation_id == org_id)
        result = await conn.execute(stmt)
        return result.scalars().all()

async def get_organisation_by_name(name: str) -> Organisation | None:
    async with db_helper.session_factory() as conn:
        stmt = select(Organisation).where(Organisation.name==name)
        result = await conn.execute(stmt)
        return result.scalar()

async def get_all_orgs() -> list[Organisation] | None:
    async with db_helper.session_factory() as conn:
        stmt = select(Organisation)
        result = await conn.execute(stmt)
        return result.scalars().all()

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
            .values(organisation_id = user.organisation_id, is_admin=user.is_admin)
            .filter_by(id=user.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def user_set_admin(user: User):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(User)
            .values(is_admin = user.is_admin)
            .filter_by(id=user.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def org_set_token(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_token = org.vk_token)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def org_set_password(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(join_password = org.join_password)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def org_set_name(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(name = org.name)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def org_set_vk_group_id(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_group_id = org.vk_group_id)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()


async def set_yd_all(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(yd_login = org.yd_login, yd_pass  = org.yd_pass, yd_station_id = org.yd_station_id,
                    yd_groups_ids = org.yd_groups_ids)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def set_organisation_yd_str(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(last_yd_str = org.last_yd_str)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def set_yd_last_pub_date(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(yd_last_pub_date = datetime.datetime.now())
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def set_vk_last_light_post(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_last_light_post = org.vk_last_light_post)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def set_last_light_post_info(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_last_light_post = org.vk_last_light_post,
                    last_create_date = org.last_create_date,
                    last_image_name = org.last_image_name)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def set_vk_last_post_id(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_last_post_id = org.vk_last_post_id, vk_last_pub_date = org.vk_last_pub_date)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def set_org_text(org: Organisation, start: bool | None = None, end: bool | None = None):
    if not start and not end:
        return None
    async with (db_helper.session_factory() as conn):
        if start:
            stmt = (
                update(Organisation)
                .values(start_text = org.start_text)
                .filter_by(id=org.id)
            )
        if end:
            stmt = (
                update(Organisation)
                .values(end_text = org.end_text)
                .filter_by(id=org.id)
            )
        await conn.execute(stmt)
        await conn.commit()

async def set_org_settings(org: Organisation, vk_pin: bool | None = None, vk_del: bool | None = None):
    if not vk_pin and not vk_del:
        return None
    async with (db_helper.session_factory() as conn):
        if vk_pin:
            stmt = (
                update(Organisation)
                .values(vk_is_pin_image = org.vk_is_pin_image)
                .filter_by(id=org.id)
            )
        if vk_del:
            stmt = (
                update(Organisation)
                .values(vk_is_delete_prev_post = org.vk_is_delete_prev_post)
                .filter_by(id=org.id)
            )
        await conn.execute(stmt)
        await conn.commit()

async def set_hashtag(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(hashtag = org.hashtag)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()

async def set_light_template(org: Organisation):
    async with (db_helper.session_factory() as conn):
        stmt = (
            update(Organisation)
            .values(vk_template = org.vk_template)
            .filter_by(id=org.id)
        )
        await conn.execute(stmt)
        await conn.commit()


async def set_statistic(org: Organisation, light_template:dict[str:str] = None):
    async with (db_helper.session_factory() as conn):
        stmt = select(Statistic).where(Statistic.organisation_id == org.id, func.date(Statistic.updated_at) == datetime.datetime.utcnow().date())
        result = await conn.execute(stmt)
        row =  result.one_or_none()
        if row:
            stmt = (
                update(Statistic)
                .values(**light_template)
                .filter_by(id=row[0].id)
            )
            await conn.execute(stmt)
            await conn.commit()
        else:
            statistic = Statistic(organisation_id = org.id, **light_template)
            conn.add(statistic)
            await conn.commit()

async def delete_user(user: User):
    async with (db_helper.session_factory() as conn):
        stmt = (
            delete(User)
            .filter_by(id=user.id)
        )
        await conn.execute(stmt)
        await conn.commit()

