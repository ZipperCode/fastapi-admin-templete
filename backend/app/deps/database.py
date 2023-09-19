from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


async def begin_transition(session: AsyncSession):
    async with session.begin() as transition:
        try:
            yield
            await transition.commit()
        except Exception as e:
            await transition.rollback()
            raise e
