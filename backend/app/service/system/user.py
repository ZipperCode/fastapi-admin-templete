import datetime
from abc import ABC, abstractmethod
from typing import Union

from fastapi import Request, Depends
from fastapi_pagination.bases import AbstractPage
from pydantic import TypeAdapter
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import add

from app.consts.http import HttpResp
from app.core.exceptions import AppException
from app.db.session import AsyncSessionLocal
from app.deps.database import get_db
from app.models import SystemUser, SystemRole, SystemDept, SystemPost
from app.schemas.system import SystemUserCreateIn, SystemUserUpdateIn, SystemUserListIn, SystemUserOut, SystemUserEditIn

__all__ = [
    'ISystemUserService', 'get_instance'
]

from app.utils import encrypt_util, url_util


class ISystemUserService(ABC):
    """系统管理员服务抽象类"""

    @abstractmethod
    async def add(self, admin_create_in: SystemUserCreateIn) -> SystemUserOut:
        pass

    @abstractmethod
    async def edit(self, admin_edit_in: SystemUserEditIn):
        pass

    @abstractmethod
    async def update(self, admin_update_in: SystemUserUpdateIn, user_id: int):
        pass

    @abstractmethod
    async def list(self, list_in: SystemUserListIn) -> AbstractPage[SystemUserOut]:
        pass

    @abstractmethod
    async def detail(self, id_: int) -> SystemUserOut:
        pass

    @abstractmethod
    async def delete(self, id_: int):
        pass

    @abstractmethod
    async def disable(self, id_: int):
        pass


class SystemUserService(ISystemUserService):
    session: AsyncSessionLocal

    def __init__(self, request: Request, session: AsyncSession):
        self.request = request
        self.session: AsyncSession = session

    async def check_user_exists(self, id_: Union[int, None] = None,
                                username: Union[str, None] = None) -> Union[None, SystemUser]:
        query = select(SystemUser)

        if id_:
            query = query.where(SystemUser.id == id_, SystemUser.is_delete == 0)
        elif username:
            query = query.where(SystemUser.username == username, SystemUser.is_delete == 0)

        return await self.session.scalar(query)

    async def add(self, admin_create_in: SystemUserCreateIn) -> SystemUserOut:
        find_user = await self.check_user_exists(username=admin_create_in.username)
        assert not find_user, "账号已存在"
        create_user = SystemUser()
        create_user.username = admin_create_in.username
        create_user.password = encrypt_util.make_md5(admin_create_in.password.strip())
        create_user.avatar = url_util.to_relative_url(admin_create_in.avatar) \
            if admin_create_in.avatar else '/api/static/backend_avatar.png'
        create_user.is_disable = admin_create_in.is_disable
        create_user.create_time = datetime.datetime.now()
        create_user.update_time = datetime.datetime.now()
        if len(admin_create_in.role_ids) > 0:
            # role
            roles = (await self.session.scalars(
                select(SystemRole).where(SystemRole.id.in_(admin_create_in.role_ids))
            )).all()
            if len(roles) > 0:
                create_user.roles.append(roles)

        if len(admin_create_in.dept_ids) > 0:
            # dept
            depts = (await self.session.scalars(
                select(SystemDept).where(SystemDept.id.in_(admin_create_in.dept_ids))
            )).all()
            if len(depts) > 0:
                create_user.depts.append(depts)
        if len(admin_create_in.post_ids) > 0:
            posts = (await self.session.scalars(
                select(SystemPost).where(SystemPost.id.in_(admin_create_in.post_ids))
            )).all()
            if len(posts) > 0:
                create_user.posts.append(posts)
        # self.session.add(create_user)
        # await self.session.commit()
        return TypeAdapter(SystemUserOut).validate_python(create_user)

    async def edit(self, admin_edit_in: SystemUserEditIn):
        find_user = await self.check_user_exists(admin_edit_in.id)
        assert find_user, "账号不存在"

    async def update(self, admin_update_in: SystemUserUpdateIn, user_id: int):
        find_user = await self.check_user_exists(user_id)

        find_user.avatar = url_util.to_relative_url(admin_update_in.avatar)
        if admin_update_in.password:
            curr_pass = encrypt_util.make_md5(admin_update_in.password)
            if curr_pass != find_user.password:
                raise AppException(HttpResp.FAILED, msg='当前密码不正确!')
            if not (6 <= len(admin_update_in.password) <= 20):
                raise AppException(HttpResp.FAILED, msg='密码必须在6~20位')
            find_user.password = curr_pass

        find_user.nickname = admin_update_in.nickname
        find_user.update_time = datetime.datetime.now()
        await self.session.commit()

    async def list(self, list_in: SystemUserListIn) -> AbstractPage[SystemUserOut]:
        query = select(SystemUser)
        if list_in.username:
            query = query.where(SystemUser.username.like(f'%{list_in.username}%'))
        if list_in.nickname:
            query = query.where(SystemUser.nickname.like(f"%{list_in.nickname}%"))

        if list_in.role:
            query = query.join(SystemUser.roles.and_(SystemRole.id == list_in.role))

    async def detail(self, id_: int) -> SystemUserOut:
        pass

    async def delete(self, id_: int):
        pass

    async def disable(self, id_: int):
        pass


def get_instance(request: Request, session: AsyncSessionLocal = Depends(get_db)):
    return SystemUserService(request, session)
