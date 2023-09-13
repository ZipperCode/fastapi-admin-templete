from pydantic.v1 import BaseSettings


class Settings(BaseSettings):

    # 数据源配置
    database_url: str = 'mysql+pymysql://root:root@localhost:3306/likeadmin?charset=utf8mb4'