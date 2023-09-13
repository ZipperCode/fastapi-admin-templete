from abc import ABC, abstractmethod
from typing import List, Union

from app.db.session import SessionLocal
from app.models.enums import MenuType
from app.models.system import system_menu
from app.schemas.system import SystemAuthMenuOut, SystemAuthMenuCreateIn, SystemAuthMenuEditIn


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

    async def select_menu_by_role_id(self, role_ids: List[int]) -> List[Union[SystemAuthMenuOut, dict]]:
        """根据角色ID获取菜单"""
        admin_id = self.request.state.admin_id
        menu_ids = await self.auth_perm_service.select_menu_ids_by_role_id(role_ids) or [0]
        where = [system_menu.c.menu_type.in_((MenuType.directory.value, MenuType.menu.value)),
                 system_menu.c.is_disable == 0]
        if admin_id != 1:
            where.append(system_menu.c.id.in_(menu_ids))


            menus = await db.fetch_all(
                system_menu.select().where(*where)
                .order_by(system_menu.c.menu_sort.desc(), system_menu.c.id))
        return ArrayUtil.list_to_tree(
            [i.dict(exclude_none=True) for i in pydantic.parse_obj_as(List[SystemAuthMenuOut], menus)],
            'id', 'pid', 'children')

    async def list(self) -> List[Union[SystemAuthMenuOut, dict]]:
        """菜单列表"""
        menus = await db.fetch_all(
            system_menu.select()
            .order_by(system_menu.c.menu_sort.desc(), system_menu.c.id))
        return ArrayUtil.list_to_tree(
            [i.dict(exclude_none=True) for i in pydantic.parse_obj_as(List[SystemAuthMenuOut], menus)],
            'id', 'pid', 'children')

    async def detail(self, id_: int) -> Union[SystemAuthMenuOut, dict]:
        """菜单详情"""
        menu = await db.fetch_one(
            system_menu.select().where(system_menu.c.id == id_).limit(1))
        assert menu, '菜单已不存在!'
        return SystemAuthMenuOut.from_orm(menu).dict(exclude_none=True)

    async def add(self, create_in: SystemAuthMenuCreateIn):
        """新增菜单"""
        create_dict = create_in.dict()
        create_dict['create_time'] = int(time.time())
        create_dict['update_time'] = int(time.time())
        await db.execute(system_menu.insert().values(**create_dict))
        await RedisUtil.delete(AdminConfig.backstage_roles_key)

    async def edit(self, edit_in: SystemAuthMenuEditIn):
        """编辑菜单"""
        assert await db.fetch_one(
            system_menu.select().where(system_menu.c.id == edit_in.id).limit(1)), '菜单已不存在!'
        edit_dict = edit_in.dict()
        edit_dict['update_time'] = int(time.time())
        await db.execute(system_menu.update().where(system_menu.c.id == edit_in.id).values(**edit_dict))
        await RedisUtil.delete(AdminConfig.backstage_roles_key)

    async def delete(self, id_: int):
        """删除菜单"""
        assert await db.fetch_one(
            system_menu.select().where(system_menu.c.id == id_).limit(1)), '菜单已不存在!'
        assert not await db.fetch_one(
            system_menu.select().where(system_menu.c.pid == id_)), '请先删除子菜单再操作！'
        await db.execute(system_menu.delete().where(system_menu.c.id == id_))
        await self.auth_perm_service.batch_delete_by_menu_id(id_)
        await RedisUtil.delete(AdminConfig.backstage_roles_key)

    def __init__(self, request: Request, auth_perm_service: ISystemAuthPermService):
        self.request: Request = request
        self.auth_perm_service: ISystemAuthPermService = auth_perm_service

    @classmethod
    async def instance(cls, request: Request,
                       auth_perm_service: ISystemAuthPermService = Depends(SystemAuthPermService.instance)):
        """实例化"""
        return cls(request, auth_perm_service)
