from sqlalchemy import URL, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

async_engine = create_async_engine(
    URL.create("mysql+aiomysql", "root", "zzp949389", "localhost", 3306, "fast_admin"), pool_recycle=1500
)

AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession)

# engine = create_engine(
#     URL.create("mysql+aiomysql", "root", "zzp949389", "localhost", 3306, "mysql"), pool_recycle=1500
# )
#
# SessionLocal = sessionmaker(engine)
