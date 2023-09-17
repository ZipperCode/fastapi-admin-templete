import logging

from fastapi import APIRouter, Depends

from app.consts.http import unified_resp
from app.deps.log import record_log
from app.schemas.system import SystemLoginIn

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/system')




# @router.post('/login')
# @unified_resp
# async def login(login_in: SystemLoginIn, login_service: ISystemLoginService = Depends(SystemLoginService.instance)):
#     """登录系统"""
#     return await login_service.login(login_in)
