from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base, as_declarative
from sqlalchemy import Column, text, Integer, DateTime, Boolean, String
from sqlalchemy.orm import declared_attr, DeclarativeBase, Mapped, mapped_column


# 数据库模型基类
# Base = declarative_base()

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, comment="主键ID")
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin:
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, comment='更新时间')
    delete_time = Column(DateTime, default=datetime.now, comment='删除时间')


class BanMixin:
    is_disable = Column(Boolean, nullable=False, server_default=text('0'), comment='是否禁用: 0=否, 1=是')


class LastLoginMixin:
    last_login_ip = Column(String(30), server_default='', comment='最后登录IP')
    last_login_time = Column(DateTime, default=datetime.now, comment='最后登录时间')


class BaseMixin(BanMixin, TimestampMixin):
    pass
