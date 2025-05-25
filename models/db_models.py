from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import func, MetaData, Boolean, String, Integer, DateTime, ForeignKey, Enum
from datetime import datetime
from typing import List
import enum

from config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

class Organisation(Base):
    __tablename__ = 'organisations'

    name: Mapped[str] = mapped_column(String, nullable=False)
    join_password: Mapped[str] = mapped_column(String, nullable=True)
    vk_token: Mapped[str] = mapped_column(String, nullable=True)
    vk_group_id: Mapped[int] = mapped_column(Integer, nullable=True)
    vk_last_light_post: Mapped[str] = mapped_column(String, nullable=True)
    vk_last_pub_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    vk_last_post_id: Mapped[int] = mapped_column(Integer, nullable=True)
    vk_is_pin_image: Mapped[bool] = mapped_column(Boolean, default=True)
    vk_is_delete_prev_post: Mapped[bool] = mapped_column(Boolean, default=0, server_default='1')
    vk_template: Mapped[str] = mapped_column(String, nullable=True)
    yd_login: Mapped[str] = mapped_column(String, nullable=True)
    yd_pass: Mapped[str] = mapped_column(String, nullable=True)
    yd_station_id: Mapped[str] = mapped_column(String, nullable=True)
    yd_groups_ids: Mapped[str] = mapped_column(String, nullable=True)
    yd_last_pub_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    hashtag: Mapped[str] = mapped_column(String, nullable=True)
    last_create_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_group_state: Mapped[str] = mapped_column(String, nullable=True)
    last_image_name: Mapped[str] = mapped_column(String, nullable=True)
    last_yd_str: Mapped[str] = mapped_column(String, nullable=True)
    start_text: Mapped[str] = mapped_column(String, nullable=True)
    end_text: Mapped[str] = mapped_column(String, nullable=True)
    notification_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    users: Mapped[List['User']] = relationship(back_populates='organisation')
    statistic: Mapped[List['Statistic']] = relationship(back_populates='organisation')

class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(String, nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    organisation_id: Mapped[int] = mapped_column(ForeignKey('organisations.id'), unique=False, nullable=True)
    organisation: Mapped['Organisation'] = relationship(back_populates='users')
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

class BloodColor(enum.Enum):
    red = 0
    yellow = 1
    green = 2

class Statistic(Base):
    __tablename__ = 'statistic'

    organisation_id: Mapped[int] = mapped_column(ForeignKey('organisations.id'), unique=False, nullable=True)
    organisation: Mapped['Organisation'] = relationship(back_populates='statistic')
    o_plus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))
    o_minus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))
    a_plus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))
    a_minus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))
    b_plus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))
    b_minus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))
    ab_plus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))
    ab_minus: Mapped[BloodColor] = mapped_column(Enum(BloodColor))


