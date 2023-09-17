from fastapi import APIRouter, Depends

from app.consts.http import unified_resp
from app.deps.log import record_log
from app.schemas.system import SystemMenuCreateIn
from app.service.system import menu
from app.service.system.menu import ISystemMenuService

router = APIRouter(prefix="/menu")


@router.post('/add', dependencies=[Depends(record_log(title='菜单新增'))])
@unified_resp
async def menu_add(create_in: SystemMenuCreateIn,
                   menu_service: ISystemMenuService = Depends(menu.get_instance)):
    """新增菜单"""
    return await menu_service.add(create_in)
