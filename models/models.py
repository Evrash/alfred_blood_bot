from poetry.core.masonry.metadata import Metadata
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, MetaData, Boolean, String, Integer, DateTime
from datetime import datetime

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
    vk_token: Mapped[str] = mapped_column(String, nullable=True)
    vk_group_id: Mapped[int] = mapped_column(Integer, nullable=True)
    vk_last_light_post: Mapped[str] = mapped_column(String, nullable=True)
    vk_is_pin_image: Mapped[bool] = mapped_column(Boolean, default=True)
    vk_template: Mapped[int] = mapped_column(Integer, nullable=True)
    yd_login: Mapped[str] = mapped_column(String, nullable=True)
    yd_pass: Mapped[str] = mapped_column(String, nullable=True)
    yd_station_id: Mapped[str] = mapped_column(String, nullable=True)
    yd_groups_ids: Mapped[str] = mapped_column(String, nullable=True)
    hashtag: Mapped[str] = mapped_column(String, nullable=True)
    last_create_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_group_state: Mapped[str] = mapped_column(String, nullable=True)
    start_text: Mapped[str] = mapped_column(String, nullable=True)
    end_text: Mapped[str] = mapped_column(String, nullable=True)
    notification_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

