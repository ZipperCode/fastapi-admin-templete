import datetime
from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any, Sequence

from fastapi import Request, Depends
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import TypeAdapter
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.database import get_db
from app.models import SystemMenu
from app.schemas.base import Page
from app.schemas.menu import SystemMenuListIn
from app.schemas.menu import SystemMenuOut, SystemMenuCreateIn, SystemMenuEditIn

__all__ = [
    'ISystemMenuService',
    'get_instance'
]


class ISystemMenuService(ABC):

    @abstractmethod
    async def add(self, create_in: SystemMenuCreateIn):
        """
        添加菜单
        :param create_in: model
        :return:
        """

    @abstractmethod
    async def delete(self, id_: int):
        """
        删除菜单
        :param id_:
        :return:
        """

    @abstractmethod
    async def edit(self, edit_in: SystemMenuEditIn):
        """
        编辑菜单
        :param edit_in:
        :return:
        """

    @abstractmethod
    async def detail(self, id_: int) -> SystemMenuOut:
        """
        菜单详情
        :param id_: 菜单id
        :return: 菜单信息
        """

    @abstractmethod
    async def list(self, list_in: SystemMenuListIn) -> Page[SystemMenuOut]:
        """
        所有菜单列表
        :return:
        """

    @abstractmethod
    async def select_menu_by_ids(self, ids: List[int]) -> List[SystemMenu]:
        """
        查询指定id的菜单列表
        :param ids 菜单id
        """

    @abstractmethod
    async def select_menu_by_role_id(self, role_ids: List[int]) -> List[SystemMenuOut]:
        """
        根据角色id查找对应的菜单
        :param role_ids: 角色id
        :return: 菜单列表
        """


class SystemMenuService(ISystemMenuService):
    async def add(self, create_in: SystemMenuCreateIn):
        create_dict = create_in.model_dump()
        create_dict['create_time'] = datetime.datetime.now()
        create_dict['update_time'] = datetime.datetime.now()
        await self.session.execute(
            insert(SystemMenu).values(**create_dict)
        )

    async def one_or_none(self, id_) -> Union[SystemMenu, None]:
        find = await self.session.get(SystemMenu, id_)
        assert find, "菜单不存在"
        return find

    async def delete(self, id_: int):
        await self.one_or_none(id_)

        count = (await self.session.execute(
            func.count(SystemMenu.id.label('total')).filter(SystemMenu.pid == id_)
        )).one().total
        assert count > 0, "请先删除子菜单再操作！"

        await self.session.execute(
            delete(SystemMenu).where(SystemMenu.id == id_)
        )

    async def edit(self, edit_in: SystemMenuEditIn):
        await self.one_or_none(edit_in.id)

        edit_dict = edit_in.model_dump()
        edit_dict['update_time'] = datetime.datetime.now()
        await self.session.execute(
            update(SystemMenu).where(SystemMenu.id == edit_in.id).values(**edit_dict)
        )

    async def detail(self, id_: int) -> SystemMenuOut:
        """菜单详情"""
        menu = await self.one_or_none(id_)
        return TypeAdapter(SystemMenuOut).validate_python(menu)

    async def list(self, list_in: SystemMenuListIn) -> Page[SystemMenuOut]:
        """菜单列表"""
        return await paginate(
            conn=self.session,
            query=select(SystemMenu).order_by(SystemMenu.menu_sort.desc(), SystemMenu.id),
            params=list_in,
            transformer=SystemMenuService.convert
        )

    @staticmethod
    async def convert(sequence: Sequence[SystemMenu]) -> Sequence[SystemMenuOut]:
        def _convert(x):
            return TypeAdapter(SystemMenuOut).validate_python(x)

        return [_convert(se) for se in sequence]

    async def select_menu_by_ids(self, ids: List[int]) -> List[SystemMenu]:
        return list(
            (await self.session.scalars(
                select(SystemMenu).where(SystemMenu.id.in_(ids))
            )).all()
        )

    async def select_menu_by_role_id(self, role_ids: List[int]) -> List[SystemMenuOut]:
        # roles = (await self.session.scalars(
        #     select(SystemMenu).where(SystemMenu.id.in_(role_ids))
        # )).all()
        #
        # admin_id = self.request.state.admin_id
        # menu_ids = await self.auth_perm_service.select_menu_ids_by_role_id(role_ids) or [0]
        # where = [system_menu.c.menu_type.in_((MenuType.directory.value, MenuType.menu.value)),
        #          system_menu.c.is_disable == 0]
        # if admin_id != 1:
        #     where.append(system_menu.c.id.in_(menu_ids))
        # menus = await get_db().fetch_all(
        #     system_menu.select().where(*where)
        #     .order_by(system_menu.c.menu_sort.desc(), system_menu.c.id))
        # return ArrayUtil.list_to_tree(
        #     [i.dict(exclude_none=True) for i in pydantic.parse_obj_as(List[SystemMenuOut], menus)],
        #     'id', 'pid', 'children')
        return []

    # @staticmethod
    # def menu_tree(menu_list: List[SystemMenu]) -> List[SystemMenuOut]:
    #     if not menu_list or len(menu_list) < 0:
    #         return []
    #     menu_tree_list: List[SystemMenuOut] = list()
    #     id_map: Dict[Any, SystemMenuOut] = {menu.id: SystemMenuOut.model_validate(menu) for menu in menu_list}
    #     for menu in menu_list:
    #         if not menu.pid or menu.pid <= 0:
    #             # root
    #             menu_tree_list.append(id_map.get(menu.id))
    #         else:
    #             # children
    #             parent = id_map.get(menu.pid)
    #             if parent:
    #                 if parent.children is None:
    #                     parent.children = []
    #                 parent.children.append(id_map.get(menu.id))
    #
    #     return menu_tree_list

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session


def get_instance(session: AsyncSession = Depends(get_db)):
    return SystemMenuService(session)
