from typing import Callable

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:zzp949389@localhost:3306/fast_admin?charset=utf8mb4"

# engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_egn = create_async_engine(SQLALCHEMY_DATABASE_URI)

# 创建session元类
async_session_local: Callable[..., AsyncSession] = sessionmaker(async_egn)
