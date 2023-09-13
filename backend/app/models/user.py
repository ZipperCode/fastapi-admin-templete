from sqlalchemy import Column, String, text, Integer, Boolean, SmallInteger

from app.models.base import BaseMixin, Base, LastLoginMixin


class User(Base, BaseMixin, LastLoginMixin):
    """用户实体"""
    __name__ = 'user'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '用户信息表',
    }

    sn = Column(Integer, nullable=False, server_default=text('0'), comment='编号')
    avatar = Column(String(200), nullable=False, server_default='', comment='头像')
    real_name = Column(String(32), nullable=False, server_default='', comment='真实姓名')
    nickname = Column(String(32), nullable=False, server_default='', comment='用户昵称')
    username = Column(String(32), nullable=False, server_default='', comment='用户账号')
    password = Column(String(32), nullable=False, server_default='', comment='用户密码')
    mobile = Column(String(32), nullable=False, server_default='', comment='用户电话')
    salt = Column(String(32), nullable=False, server_default='', comment='加密盐巴')
    sex = Column(SmallInteger, nullable=True, server_default=text('0'), comment='用户性别: [1=男, 2=女]')
    is_delete = Column(Boolean, nullable=False, server_default=text('0'), comment='是否删除: [0=否, 1=是]')


user_table = User.__table__
