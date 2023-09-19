from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

import pydantic
from fastapi import Depends
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import TypeAdapter
from sqlalchemy import select, insert, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.database import get_db, begin_transition
from app.models import SystemRole, SystemMenu, SystemRoleMenu, SystemUserRole
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
            find = await self.session.execute(
                select(SystemRole).where(SystemRole.name == create_in.name.strip()).limit(1)
            )
            assert not find.scalar_one_or_none(), "角色名称已存在!"

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
        one_result = (await self.session.execute(
            select(SystemRole).where(SystemRole.id == id_).limit(1)
        )).scalar_one_or_none()
        assert one_result, "角色不存在"

        role_menus = await self.session.scalars(
            select(SystemRoleMenu.menu_id).where(SystemRoleMenu.role_id == id_)
        )

        role_dict = dict(one_result)
        menu_ids = list(map(lambda x: x[0], role_menus.all()))
        role_dict['menus'] = menu_ids

        return SystemRoleDetailOut(**role_dict)

    async def edit(self, edit_in: SystemRoleEditIn):
        """编辑角色"""
        with begin_transition(self.session):
            execute_result = await self.session.execute(
                select(SystemRole).where(SystemRole.id == edit_in.id).limit(1)
            )

            role: SystemRole = execute_result.scalar_one_or_none()
            assert role, "角色不存在!"
            assert role.name != edit_in.name.strip(), "角色名称已存在"
            # 删除所有关联的菜单
            await self.session.execute(
                delete(SystemRoleMenu).where(SystemRoleMenu.role_id == edit_in.id)
            )
            # 插入新菜单关联
            for menu_id in edit_in.menu_ids.split(","):
                await self.session.execute(
                    insert(SystemRoleMenu).values(**{
                        "role_id": edit_in.id,
                        'menu_id': int(menu_id)
                    })
                )

            # 更新菜单信息
            role_dict = edit_in.model_dump()
            role_dict['name'] = edit_in.name.strip()
            role_dict['update_time'] = datetime.now()
            del role_dict['menu_ids']

            await self.session.execute(
                update(SystemRole).where(SystemRole.id == edit_in.id).values(**role_dict)
            )

    async def delete(self, id_: int):
        """删除角色"""
        with begin_transition(self.session):
            role = (await self.session.execute(
                select(SystemRole).where(SystemRole.id == id_).limit(1)
            )).one_or_none()
            assert role, "角色不存在!"

            exe_result = await self.session.execute(
                select(SystemUserRole).with_only_columns(SystemUserRole.role_id)
                .where(SystemUserRole.role_id == id_)
                .limit(1)
            )

            assert not exe_result.one_or_none(), "角色被用户所使用，请先同用户取消关联"

            await self.session.execute(
                delete(SystemRoleMenu).where(SystemRoleMenu.role_id == id_)
            )

            await self.session.execute(
                delete(SystemRole).where(SystemRole.id == id_)
            )

    def __init__(self, session: AsyncSession, menu_service: ISystemMenuService):
        self.session: AsyncSession = session
        self.menu_service: ISystemMenuService = menu_service


def get_instance(session: AsyncSession = Depends(get_db),
                 menu_service: ISystemMenuService = Depends(menu.get_instance)):
    return SystemRoleService(session, menu_service)
