from fastapi import APIRouter, Depends

from app.consts.http import unified_resp
from app.deps.log import record_log
from app.schemas.base import Page
from app.schemas.menu import *
from app.service.system import menu
from app.service.system.menu import ISystemMenuService

router = APIRouter(prefix="/menu")

tags = ["菜单"]


@router.post(
    '/add',
    tags=tags,
    dependencies=[Depends(record_log(title='菜单新增'))]
)
@unified_resp
async def menu_add(create_in: SystemMenuCreateIn,
                   service: ISystemMenuService = Depends(menu.get_instance)):
    """新增菜单"""
    return await service.add(create_in)


@router.post(
    '/edit',
    tags=tags,
    dependencies=[Depends(record_log(title='菜单修改'))]
)
@unified_resp
async def menu_edit(edit_in: SystemMenuEditIn, service: ISystemMenuService = Depends(menu.get_instance)):
    """编辑菜单"""
    return await service.edit(edit_in)


@router.post(
    '/del',
    tags=tags,
    dependencies=[Depends(record_log(title='菜单删除'))]
)
@unified_resp
async def delete(del_in: SystemMenuDelIn,
                 service: ISystemMenuService = Depends(menu.get_instance)):
    return await service.delete(del_in.id)


@router.post(
    '/detail',
    tags=tags,
    dependencies=[Depends(record_log(title='菜单详情'))]
)
@unified_resp
async def detail(detail_in: SystemMenuDetailIn,
                 service: ISystemMenuService = Depends(menu.get_instance)):
    return await service.detail(detail_in.id)


@router.post(
    '/list',
    tags=tags,
    dependencies=[Depends(record_log(title='菜单分页列表'))],
    response_model=Page[SystemMenuOut]
)
@unified_resp
async def menu_list(list_in: SystemMenuListIn,
                 service: ISystemMenuService = Depends(menu.get_instance)):
    return await service.list(list_in)
