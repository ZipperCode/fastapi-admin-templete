from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

import pydantic
from fastapi import Depends
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import TypeAdapter
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.database import get_db
from app.models import SystemRole, SystemMenu
from app.schemas.base import Page
from app.schemas.role import *
from app.service.system import menu
from app.service.system.menu import ISystemMenuService


class ISystemRoleService(ABC):
    """系统角色服务抽象类"""

    @abstractmethod
    async def all(self) -> List[SystemRoleOut]:
        pass

    @abstractmethod
    async def list(self, list_in: SystemRoleListIn) -> AbstractPage[SystemRoleDetailOut]:
        pass

    @abstractmethod
    async def detail(self, id_: int) -> SystemRoleDetailOut:
        pass

    @abstractmethod
    async def add(self, create_in: SystemRoleCreateIn):
        pass

    @abstractmethod
    async def edit(self, edit_in: SystemRoleEditIn):
        pass

    @abstractmethod
    async def delete(self, id_: int):
        pass


class SystemRoleService(ISystemRoleService):
    """系统角色服务实现类"""

    async def one_or_none(self, id_: int) -> SystemRole:
        return await self.session.scalar(
            select(SystemRole).where(SystemRole.id == id_)
        )

    async def add(self, create_in: SystemRoleCreateIn):
        async with self.session.begin() as transition:
            find = await self.session.scalar(
                select(SystemRole).where(SystemRole.name == create_in.name.strip()).limit(1)
            )
            assert not find, "角色名称已存在!"

            role_dict = create_in.model_dump()
            role_dict['name'] = create_in.name.strip()
            role_dict['create_time'] = datetime.now()
            role_dict['update_time'] = datetime.now()

            insert_result = await self.session.execute(
                insert(SystemRole).values(**role_dict)
            )

            role_id = insert_result.inserted_primary_key

            menu_ids = list(map(lambda x: int(x), create_in.menu_ids.strip().split(",")))
            if len(menu_ids) > 0:
                q_menus = await self.session.execute(
                    select(SystemMenu).with_only_columns(SystemMenu.id).where(SystemMenu.id.in_(menu_ids))
                )
                for m_row in q_menus.all():
                    menu_id = m_row[0]
                    await self.session.execute(
                        insert(SystemMenu).values({
                            'role_id': role_id,
                            'menu_id': menu_id
                        })
                    )
            await transition.commit()

    async def all(self) -> List[SystemRoleOut]:
        """角色所有"""
        scalar_result = await self.session.scalars(
            select(SystemRole).order_by(SystemRole.sort.desc())
        )
        return TypeAdapter(List[SystemRoleOut]).validate_python(scalar_result.all())

    async def list(self, list_in: SystemRoleListIn) -> Page[SystemRoleDetailOut]:
        """角色列表"""

        async def convert(sequence):
            return [TypeAdapter(SystemRoleDetailOut).validate_python(x) for x in sequence]

        return await paginate(
            self.session,
            select(SystemRole).order_by(SystemRole.sort.desc()),
            params=list_in,
            transformer=convert
        )

    async def detail(self, id_: int) -> SystemRoleDetailOut:
        """角色详情"""
        one_result = await self.session.get(SystemRole, id_)


        role = await db.fetch_one(system_auth_role.select().where(system_auth_role.c.id == id_).limit(1))
        assert role, '角色已不存在!'
        role_id = role.id
        role_dict = dict(role)
        role_dict['member'] = await self.get_member_cnt(role_id)
        role_dict['menus'] = await self.auth_perm_service.select_menu_ids_by_role_id([role_id])
        return SystemRoleDetailOut(**role_dict)

    @db.transaction()
    async def edit(self, edit_in: SystemRoleEditIn):
        """编辑角色"""
        assert await db.fetch_one(
            system_auth_role.select().where(system_auth_role.c.id == edit_in.id)
            .limit(1)), '角色已不存在!'
        assert not await db.fetch_one(
            system_auth_role.select()
            .where(system_auth_role.c.id != edit_in.id,
                   system_auth_role.c.name == edit_in.name.strip())
            .limit(1)), '角色名称已存在!'
        role_dict = edit_in.dict()
        role_dict['name'] = edit_in.name.strip()
        role_dict['update_time'] = int(time.time())
        del role_dict['menu_ids']
        await db.execute(
            system_auth_role.update().where(system_auth_role.c.id == edit_in.id).values(**role_dict))
        await self.auth_perm_service.batch_delete_by_role_id(edit_in.id)
        await self.auth_perm_service.batch_save_by_menu_ids(edit_in.id, edit_in.menu_ids)
        await self.auth_perm_service.cache_role_menus_by_role_id(edit_in.id)

    @db.transaction()
    async def delete(self, id_: int):
        """删除角色"""
        assert await db.fetch_one(
            system_auth_role.select().where(system_auth_role.c.id == id_)
            .limit(1)), '角色已不存在!'
        assert not await db.fetch_one(
            system_auth_admin.select()
            .where(func.find_in_set(id_, system_auth_admin.c.role_ids), system_auth_admin.c.is_delete == 0)
            .limit(1)), '角色已被管理员使用,请先移除'
        await db.execute(system_auth_role.delete().where(system_auth_role.c.id == id_))
        await self.auth_perm_service.batch_delete_by_role_id(id_)
        await RedisUtil.hdel(AdminConfig.backstage_roles_key, str(id_))

    def __init__(self, session: AsyncSession, menu_service: ISystemMenuService):
        self.session: AsyncSession = session
        self.menu_service: ISystemMenuService = menu_service


def get_instance(session: AsyncSession = Depends(get_db),
                 menu_service: ISystemMenuService = Depends(menu.get_instance)):
    return SystemRoleService(session, menu_service)
