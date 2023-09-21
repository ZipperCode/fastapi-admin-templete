from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_db():
    yield AsyncSessionLocal()


async def with_transition(session: AsyncSession):
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


async def begin_transition() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield
        except Exception as e:
            await session.rollback()
            raise e
