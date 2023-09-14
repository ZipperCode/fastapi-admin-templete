import time
from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any

import pydantic
from fastapi import Request, Depends
from pydantic import TypeAdapter
from sqlalchemy import select

from app.db.session import SessionLocal
from app.deps.database import create_session
from app.models import system_menu, SystemMenu
from app.models.enums import MenuType
from app.schemas.system import SystemAuthMenuOut, SystemAuthMenuCreateIn, SystemAuthMenuEditIn
from app.utils.array_util import ArrayUtil


class ISystemMenuService(ABC):
    @abstractmethod
    async def select_menu_by_role_id(self, role_ids: List[int]) -> List[Union[SystemAuthMenuOut, dict]]:
        """
        根据角色id查找对应的菜单
        :param role_ids: 角色id
        :return: 菜单列表
        """

    @abstractmethod
    async def list(self) -> List[Union[SystemAuthMenuOut, dict]]:
        """
        所有菜单列表
        :return:
        """

    @abstractmethod
    async def detail(self, id_: int) -> Union[SystemAuthMenuOut, dict]:
        """
        菜单详情
        :param id_: 菜单id
        :return: 菜单信息
        """

    @abstractmethod
    async def add(self, create_in: SystemAuthMenuCreateIn):
        """
        添加菜单
        :param create_in: model
        :return:
        """

    @abstractmethod
    async def edit(self, edit_in: SystemAuthMenuEditIn):
        """
        编辑菜单
        :param edit_in:
        :return:
        """

    @abstractmethod
    async def delete(self, id_: int):
        """
        删除菜单
        :param id_:
        :return:
        """


class SystemAuthMenuService(ISystemMenuService):
    """系统菜单服务实现类"""

    def __init__(self, request: Request):
        self.request: Request = request

    async def select_menu_by_role_id(self, role_ids: List[int]) -> List[Union[SystemAuthMenuOut, dict]]:
        admin_id = self.request.state.admin_id
        menu_ids = await self.auth_perm_service.select_menu_ids_by_role_id(role_ids) or [0]
        where = [system_menu.c.menu_type.in_((MenuType.directory.value, MenuType.menu.value)),
                 system_menu.c.is_disable == 0]
        if admin_id != 1:
            where.append(system_menu.c.id.in_(menu_ids))
        menus = await get_db().fetch_all(
            system_menu.select().where(*where)
            .order_by(system_menu.c.menu_sort.desc(), system_menu.c.id))
        return ArrayUtil.list_to_tree(
            [i.dict(exclude_none=True) for i in pydantic.parse_obj_as(List[SystemAuthMenuOut], menus)],
            'id', 'pid', 'children')

    async def list(self) -> List[Union[SystemAuthMenuOut, dict]]:
        """菜单列表"""

        with SessionLocal() as session:
            menu_result = session.scalars(
                select(SystemMenu).order_by(SystemMenu.menu_sort.desc(), SystemMenu.id)
            )


        menus = await self.db.fetch_all(
            system_menu.select().order_by(system_menu.c.menu_sort.desc(), system_menu.c.id)
        )
        serial = TypeAdapter(List[SystemMenu]).validate_python(menus)
        return ArrayUtil.list_to_tree(
            [i.model_dump(exclude_none=True) for i in pydantic.parse_obj_as(List[SystemAuthMenuOut], menus)],
            'id', 'pid', 'children')

    async def detail(self, id_: int) -> Union[SystemAuthMenuOut, dict]:
        """菜单详情"""
        menu = await self.db.fetch_one(
            system_menu.select().where(system_menu.c.id == id_).limit(1))
        assert menu, '菜单已不存在!'
        return SystemAuthMenuOut.from_orm(menu).dict(exclude_none=True)

    async def add(self, create_in: SystemAuthMenuCreateIn):
        """新增菜单"""
        create_dict = create_in.dict()
        create_dict['create_time'] = int(time.time())
        create_dict['update_time'] = int(time.time())
        await self.db.execute(system_menu.insert().values(**create_dict))
        await RedisUtil.delete(AdminConfig.backstage_roles_key)

    async def edit(self, edit_in: SystemAuthMenuEditIn):
        """编辑菜单"""
        assert await self.db.fetch_one(
            system_menu.select().where(system_menu.c.id == edit_in.id).limit(1)), '菜单已不存在!'
        edit_dict = edit_in.dict()
        edit_dict['update_time'] = int(time.time())
        await self.db.execute(system_menu.update().where(system_menu.c.id == edit_in.id).values(**edit_dict))
        await RedisUtil.delete(AdminConfig.backstage_roles_key)

    async def delete(self, id_: int):
        """删除菜单"""
        assert await self.db.fetch_one(
            system_menu.select().where(system_menu.c.id == id_).limit(1)), '菜单已不存在!'
        assert not await self.db.fetch_one(
            system_menu.select().where(system_menu.c.pid == id_)), '请先删除子菜单再操作！'
        await self.db.execute(system_menu.delete().where(system_menu.c.id == id_))
        await self.auth_perm_service.batch_delete_by_menu_id(id_)
        await RedisUtil.delete(AdminConfig.backstage_roles_key)

    @classmethod
    async def instance(cls, request: Request, db: Database = Depends(get_db)):
        """实例化"""
        return cls(request, db)

    @staticmethod
    def menu_tree(menu_list: List[SystemMenu]) -> List[SystemAuthMenuOut]:
        if not menu_list or len(menu_list) < 0:
            return []
        menu_tree_list: List[SystemAuthMenuOut] = list()
        id_map: Dict[Any, SystemAuthMenuOut] = {menu.id: SystemAuthMenuOut.model_validate(menu) for menu in menu_list}
        for menu in menu_list:
            if not menu.pid or menu.pid <= 0:
                # root
                menu_tree_list.append(id_map.get(menu.id))
            else:
                # children
                parent = id_map.get(menu.pid)
                if parent:
                    if parent.children is None:
                        parent.children = []
                    parent.children.append(id_map.get(menu.id))

        return menu_tree_list
