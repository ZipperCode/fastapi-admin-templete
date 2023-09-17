import re
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base, as_declarative
from sqlalchemy import Column, text, Integer, DateTime, Boolean, String
from sqlalchemy.orm import declared_attr, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __table_args__ = {"mysql_engine": "InnoDB"}
    __mapper_args__ = {"eager_defaults": True}

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r"(?P<key>[A-Z])", r"_\g<key>", cls.__name__).lower().strip('_')

    id: Mapped[int] = mapped_column(primary_key=True, comment="主键ID", autoincrement=True)


class TimestampMixin:
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='更新时间')


class BanMixin:
    is_disable: Mapped[Optional[bool]] = Column(Boolean, server_default=text('0'), comment='是否禁用: 0=否, 1=是')


class DeleteMixin:
    is_delete: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('0'),
                                                      comment='是否删除: [0=否, 1=是]')
    delete_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='删除时间')


class LastLoginMixin:
    last_login_ip: Mapped[Optional[str]] = Column(String(30), server_default='', comment='最后登录IP')
    last_login_time: Mapped[Optional[datetime]] = Column(DateTime, default=datetime.now, comment='最后登录时间')


class BaseMixin(BanMixin, TimestampMixin):
    pass
