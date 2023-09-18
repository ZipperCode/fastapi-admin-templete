from fastapi import APIRouter, Depends

from app.consts.http import unified_resp
from app.deps.log import record_log
from app.schemas.base import Page
from app.schemas.role import *
from app.service.system import role
from app.service.system.role import ISystemRoleService

router = APIRouter(prefix="/role")

tags = ["角色"]


@router.post(
    '/add',
    tags=tags,
    dependencies=[Depends(record_log(title='角色新增'))]
)
@unified_resp
async def role_add(create_in: SystemRoleCreateIn,
                   service: ISystemRoleService = Depends(role.get_instance)):
    """新增角色"""
    return await service.add(create_in)


@router.post(
    '/edit',
    tags=tags,
    dependencies=[Depends(record_log(title='角色修改'))]
)
@unified_resp
async def role_edit(edit_in: SystemRoleEditIn, service: ISystemRoleService = Depends(role.get_instance)):
    """编辑角色"""
    return await service.edit(edit_in)


@router.post(
    '/del',
    tags=tags,
    dependencies=[Depends(record_log(title='角色删除'))]
)
@unified_resp
async def delete(del_in: SystemRoleDelIn,
                 service: ISystemRoleService = Depends(role.get_instance)):
    return await service.delete(del_in.id)


@router.post(
    '/detail',
    tags=tags,
    dependencies=[Depends(record_log(title='角色详情'))]
)
@unified_resp
async def detail(detail_in: SystemRoleDetailIn,
                 service: ISystemRoleService = Depends(role.get_instance)):
    return await service.detail(detail_in.id)


@router.post(
    '/list',
    tags=tags,
    dependencies=[Depends(record_log(title='角色分页列表'))],
    response_model=Page[SystemRoleOut]
)
@unified_resp
async def role_list(list_in: SystemRoleListIn,
                    service: ISystemRoleService = Depends(role.get_instance)):
    return await service.list(list_in)
