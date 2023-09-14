from sqlalchemy import Column, String, text, Integer, Boolean, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseMixin, Base, LastLoginMixin


class User(Base, BaseMixin, LastLoginMixin):
    """用户实体"""
    __name__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True, comment="主键ID")

    sn: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='编号')
    avatar: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='头像')
    real_name: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='真实姓名')
    nickname: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='用户昵称')
    username: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='用户账号')
    password: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='用户密码')
    mobile: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='用户电话')
    salt: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='加密盐巴')
    sex = Column(SmallInteger, nullable=True, server_default=text('0'), comment='用户性别: [1=男, 2=女]')
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                            comment='是否删除: [0=否, 1=是]')


user_table = User.__table__
