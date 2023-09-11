import asyncio

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.globals.http import HttpResp


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, timeout: int = 15):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError:
            return JSONResponse(
                {'code': HttpResp.SYSTEM_TIMEOUT_ERROR.code, 'msg': HttpResp.SYSTEM_TIMEOUT_ERROR.msg, 'data': []})
