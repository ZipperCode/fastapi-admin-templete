import os
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from app.config import get_settings


def register_redis(app: FastAPI):
    from fastapi_cache import FastAPICache
    from app.globals.cache import redis_be

    settings = get_settings()
    """
        把redis挂载到app对象上面
        :param app:
        :return:
        """

    @app.on_event('startup')
    async def startup_event():
        """
        获取链接
        :return:
        """
        app.state.redis = redis_be
        FastAPICache.init(redis_be, prefix=settings.redis_prefix)

    @app.on_event('shutdown')
    async def shutdown_event():
        """
        关闭
        :return:
        """
        app.state.redis.close()
        await app.state.redis.wait_closed()


def configure_event(app: FastAPI):
    """配置事件处理, 并初始化三方库"""

    from .config import get_settings
    from app.globals.database import db

    settings = get_settings()

    @app.on_event('startup')
    async def startup():
        await db.connect()

    @app.on_event('shutdown')
    async def shutdown():
        await db.disconnect()


def configure_middleware(app: FastAPI):
    """配置中间件"""
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    from .middlewares import init_cors_middleware, init_timeout_middleware
    app.add_middleware(ProxyHeadersMiddleware)
    init_cors_middleware(app)
    init_timeout_middleware(app)


def configure_static(app: FastAPI):
    """配置静态资源"""
    from .config import get_settings
    settings = get_settings()
    # 上传路径创建
    if not os.path.exists(settings.upload_directory):
        os.makedirs(settings.upload_directory)
    # 上传路径配置
    app.mount(settings.upload_prefix, StaticFiles(directory=settings.upload_directory), name='upload')
    # 静态资源路径配置
    if settings.enabled_static:
        app.mount(settings.static_path, StaticFiles(directory=settings.static_directory), name='static')


def configure_admin_router(app: FastAPI, prefix='/api'):
    """配置后台路由"""
    from .globals.verify import verify_token, verify_show_mode
    from .config import get_settings
    from admin.routers import user, common, system, monitor, setting, decorate
    from .generator.routers import gen

    settings = get_settings()
    # 后台依赖
    admin_deps = [Depends(verify_token)]
    if settings.disallow_modify:
        admin_deps.append(Depends(verify_show_mode))
    # admin
    app.include_router(user.router, prefix=prefix, dependencies=admin_deps)
    app.include_router(common.router, prefix=prefix, dependencies=admin_deps)
    app.include_router(system.router, prefix=prefix, dependencies=admin_deps)
    app.include_router(monitor.router, prefix=prefix, dependencies=admin_deps)
    app.include_router(setting.router, prefix=prefix, dependencies=admin_deps)
    # app.include_router(article.router, prefix=prefix, dependencies=admin_deps)
    # app.include_router(channel.router, prefix=prefix, dependencies=admin_deps)
    app.include_router(decorate.router, prefix=prefix, dependencies=admin_deps)
    # gen
    app.include_router(gen.router, prefix=prefix, dependencies=admin_deps)


def create_app() -> FastAPI:
    """创建FastAPI后台应用,并初始化"""
    from .exceptions.configuration import configure_exception

    app = FastAPI()
    configure_static(app)
    configure_exception(app)
    configure_event(app)
    configure_middleware(app)
    configure_admin_router(app)
    add_pagination(app)
    return app
