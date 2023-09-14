from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, text, Integer, DateTime, Boolean, Enum, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, BaseMixin, LastLoginMixin

__all__ = [
    'SystemConfig', 'SystemAdminUser', 'SystemMenu', 'SystemRoleMenu', 'SystemRole', 'SystemLogLogin',
    'SystemLogOperate', 'SystemDept', 'SystemPost',
    'system_config', 'system_admin_user', 'system_menu', 'system_role_menu', 'system_role',
    'system_log_login', 'system_log_operate', 'system_post', 'system_dept',
]

from .enums import MenuType


class SystemConfig(Base, BaseMixin):
    """系统全局配置表"""
    __name__ = 'system_config'
    type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, server_default='', comment='类型')
    name: Mapped[str] = mapped_column(String(60), nullable=False, server_default='', comment='键')
    value: Mapped[str] = mapped_column(Text, nullable=True, comment='值')


class SystemAdminUser(Base, BaseMixin, LastLoginMixin):
    """系统管理成员表"""
    __name__ = "system_admin_user"
    username: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='用户账号')
    nickname: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, server_default='', comment='用户昵称')
    password: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='用户密码')
    avatar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, server_default='', comment='用户头像')
    role_ids: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, server_default='', comment='角色主键')
    dept_ids: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, server_default='', comment='部门ID')
    post_ids: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, server_default='', comment='岗位ID')
    salt: Mapped[str] = mapped_column(String(20), nullable=False, server_default='', comment='加密盐巴')
    sort: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='排序编号')
    is_multipoint: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                                comment='多端登录: 0=否, 1=是')
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                            comment='是否删除: [0=否, 1=是]')


class SystemMenu(Base, BaseMixin):
    """系统菜单管理表"""
    __name__ = 'system_menu'
    pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, server_default=text('0'), comment='上级菜单')
    menu_type: Mapped[MenuType] = mapped_column(Enum(MenuType), nullable=False,
                                                server_default=str(MenuType.directory.value),
                                                comment='菜单类型: [D=目录，M=菜单，B=按钮]')
    menu_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='菜单名称')
    menu_icon: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='菜单图标')
    menu_sort: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='菜单排序')
    perms: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='权限标识')
    paths: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='路由地址')
    component: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='前端组件')
    selected: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='选中路径')
    params: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='路由参数')
    is_cache: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                           comment='是否缓存: 0=否, 1=是')
    is_show: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('1'),
                                          comment='是否显示: 0=否, 1=是')


class SystemRoleMenu(Base, BaseMixin):
    """系统角色菜单实体"""
    __name__ = 'system_role_menu'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'comment': '系统角色菜单表',
    }
    role_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='角色ID')
    menu_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='菜单ID')


class SystemRole(Base, BaseMixin):
    """系统角色实体"""
    __name__ = 'system_role'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '系统角色管理表',
    }

    name: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='角色名称')
    remark: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='备注信息')
    sort: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='角色排序')


class SystemDept(Base, BaseMixin):
    __name__ = 'system_dept'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '系统部门管理表',
    }
    pid: Mapped[int] = mapped_column(Integer, nullable=True, server_default=text('0'), comment='上级主键')
    name: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='部门名称')
    duty: Mapped[str] = mapped_column(String(30), nullable=False, server_default='', comment='负责人名')
    mobile: Mapped[str] = mapped_column(String(30), nullable=False, server_default='', comment='联系电话')
    sort: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='排序编号')
    is_stop: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                          comment='是否停用: 0=否, 1=是')
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                            comment='是否删除: [0=否, 1=是]')


class SystemPost(Base, BaseMixin):
    __name__ = 'system_post'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '系统岗位管理表',
    }
    code: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text('0'), comment='岗位编码')
    name: Mapped[str] = mapped_column(String(30), nullable=False, server_default='', comment='岗位名称')
    remarks: Mapped[str] = mapped_column(String(250), nullable=True, comment='岗位备注')
    sort: Mapped[int] = mapped_column(Integer, nullable=True, server_default=text('0'), comment='排序编号')
    is_stop: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                          comment='是否停用: 0=否, 1=是')
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('0'),
                                            comment='是否删除: [0=否, 1=是]')


class SystemLogLogin(Base):
    """系统登录日志实体"""
    __name__ = 'system_log_login'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '系统登录日志表',
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='主键')
    admin_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='管理员ID')
    username: Mapped[str] = mapped_column(String(32), nullable=False, server_default='', comment='登录账号')
    ip: Mapped[str] = mapped_column(String(30), nullable=False, server_default='', comment='登录地址')
    os: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='操作系统')
    browser: Mapped[str] = mapped_column(String(100), nullable=False, server_default='', comment='浏览器')
    status = Column(SmallInteger, nullable=False, server_default=text('0'),
                    comment='操作状态: 1=成功, 2=失败')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')


class SystemLogOperate(Base):
    """系统操作日志实体"""
    __name__ = 'la_system_log_operate'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '系统操作日志表',
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='主键')
    admin_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='操作人ID')
    type: Mapped[str] = mapped_column(String(30), nullable=False, server_default='', comment='请求类型: GET/POST/PUT')
    title: Mapped[str] = mapped_column(String(30), server_default='', comment='操作标题')
    ip: Mapped[str] = mapped_column(String(30), nullable=False, server_default='', comment='请求IP')
    url: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='请求接口')
    method: Mapped[str] = mapped_column(String(200), nullable=False, server_default='', comment='请求方法')
    args = Column(Text, comment='请求参数')
    error = Column(Text, comment='错误信息')
    status = Column(SmallInteger, nullable=False, server_default=text('1'),
                    comment='执行状态: 1=成功, 2=失败')
    start_time = Column(DateTime, nullable=False, server_default=text('0'), comment='开始时间')
    end_time = Column(DateTime, nullable=False, server_default=text('0'), comment='结束时间')
    task_time: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='执行耗时')
    create_time = Column(DateTime, nullable=True, server_default=text('0'), comment='创建时间')


system_config = SystemConfig.__table__
system_admin_user = SystemAdminUser.__table__
system_menu = SystemMenu.__table__
system_role_menu = SystemRoleMenu.__table__
system_role = SystemRole.__table__
system_post = SystemPost.__table__
system_dept = SystemDept.__table__
system_log_login = SystemLogLogin.__table__
system_log_operate = SystemLogOperate.__table__
