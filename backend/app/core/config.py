from functools import lru_cache

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # 数据源配置
    database_url: str = 'mysql+pymysql://root:zzp949389@localhost:3306/fast_admin?charset=utf8mb4'
    # 数据库连接池最小值
    database_pool_min_size: int = 5
    # 数据库连接池最大值
    database_pool_max_size: int = 20
    # 数据库连接最大空闲时间
    database_pool_recycle: int = 300


@lru_cache()
def get_settings() -> Settings:
    """获取并缓存应用配置"""
    return Settings()
