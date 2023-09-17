import os

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.staticfiles import StaticFiles

from app.api import system, user
from app.core.exceptions import configure_exception


def register_event(app: FastAPI):
    from app.db.session import engine

    @app.on_event('startup')
    async def startup():
        engine.connect()

    @app.on_event('shutdown')
    async def shutdown():
        engine.dispose()


def configure_dir(app: FastAPI):
    """配置静态资源"""
    from app.core.config import get_settings
    settings = get_settings()
    # 上传路径创建
    if not os.path.exists(settings.upload_directory):
        os.makedirs(settings.upload_directory)
    # 上传路径配置
    app.mount(settings.upload_prefix, StaticFiles(directory=settings.upload_directory), name='upload')
    # 静态资源路径配置
    if not os.path.exists(settings.static_directory):
        os.makedirs(settings.static_directory)
    app.mount(settings.static_path, StaticFiles(directory=settings.static_directory), name='static')


def configuration_router(app: FastAPI, prefix="/api"):
    app.include_router(system.router, prefix=prefix)
    app.include_router(user.router, prefix=prefix)


def create_app() -> FastAPI:
    app = FastAPI()
    configure_dir(app)
    configuration_router(app)
    configure_exception(app)
    add_pagination(app)
    return app
