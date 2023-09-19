from fastapi import APIRouter, Depends

from app.consts.http import unified_resp, AppResponse
from app.deps.log import record_log
from app.schemas.base import Page
from app.schemas.system import SystemUserCreateIn, SystemUserUpdateIn, SystemUserEditIn, SystemUserDetailIn, \
    SystemUserDelIn, SystemUserOut, SystemUserListIn
from app.service.system.user import ISystemUserService, get_instance

router = APIRouter(prefix='/user')

tags = ["用户接口"]


@router.post(
    '/add',
    description="新增用户",
    tags=tags,
    response_model=SystemUserOut,
    dependencies=[Depends(record_log(title='新增用户'))]
)
@unified_resp
async def user_add(
        admin_create_in: SystemUserCreateIn,
        service: ISystemUserService = Depends(get_instance)):
    """管理员新增"""
    return await service.add(admin_create_in)


@router.post('/edit', tags=tags, dependencies=[Depends(record_log(title='修改用户信息'))])
@unified_resp
async def user_edit(admin_edit_in: SystemUserEditIn,
                    service: ISystemUserService = Depends(get_instance)):
    """管理员更新"""
    return await service.edit(admin_edit_in)


@router.get('/detail', tags=tags, )
@unified_resp
async def admin_detail(detail_in: SystemUserDetailIn = Depends(),
                       service: ISystemUserService = Depends(get_instance)):
    """管理员详细"""
    return await service.detail(detail_in.id)


@router.post('/del', tags=tags, dependencies=[Depends(record_log(title='管理员删除'))])
@unified_resp
async def admin_del(admin_del_in: SystemUserDelIn,
                    service: ISystemUserService = Depends(get_instance)):
    """管理员删除"""
    return await service.delete(admin_del_in.id)


@router.get('/admin/list', tags=tags, response_model=Page[SystemUserOut])
@unified_resp
async def admin_list(list_in: SystemUserListIn = Depends(),
                     service: ISystemUserService = Depends(get_instance)):
    """管理员列表"""
    return await service.list(list_in)
