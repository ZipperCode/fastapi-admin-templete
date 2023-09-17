from app.db.session import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
