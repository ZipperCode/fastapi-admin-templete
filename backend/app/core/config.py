from functools import lru_cache
from os import path

from pydantic.v1 import BaseSettings

__all__ = ['get_settings']
ROOT_PATH = path.dirname(path.abspath(path.join(__file__, '..')))


class Settings(BaseSettings):
    # 数据源配置
    database_url: str = 'mysql+pymysql://root:zzp949389@localhost:3306/fast_admin?charset=utf8mb4'
    # 数据库连接池最小值
    database_pool_min_size: int = 5
    # 数据库连接池最大值
    database_pool_max_size: int = 20
    # 数据库连接最大空闲时间
    database_pool_recycle: int = 300

    # 上传文件路径
    upload_directory: str = '/tmp/uploads/'
    # 上传图片限制
    upload_image_size = 1024 * 1024 * 10
    # 上传视频限制
    upload_video_size = 1024 * 1024 * 30
    # 上传图片扩展
    upload_image_ext = {'png', 'jpg', 'jpeg', 'gif', 'ico', 'bmp'}
    # 上传视频扩展
    upload_video_ext = {'mp4', 'mp3', 'avi', 'flv', 'rmvb', 'mov'}
    # 上传路径URL前缀
    upload_prefix = '/api/uploads'

    # 静态资源URL路径
    static_path: str = '/api/static'
    # 静态资源本地路径
    static_directory: str = path.join(ROOT_PATH, 'static')


@lru_cache()
def get_settings() -> Settings:
    """获取并缓存应用配置"""
    return Settings()
