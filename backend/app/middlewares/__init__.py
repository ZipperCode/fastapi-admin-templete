import json

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.middlewares.timeout import TimeoutMiddleware

__all__ = ['init_cors_middleware', 'init_timeout_middleware']


def init_cors_middleware(app: FastAPI):
    """初始化 CORS（跨域资源共享）中间件"""
    from app.config import get_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=json.loads(get_settings().cors_allow_origins),
        allow_headers=['*'],
        allow_methods=['OPTIONS', 'GET', 'POST', 'DELETE', 'PUT'],
        max_age=3600
    )


def init_timeout_middleware(app: FastAPI):
    """初始化 超时处理 中间件"""
    from app.config import get_settings
    app.add_middleware(
        TimeoutMiddleware,
        timeout=get_settings().request_timeout)
