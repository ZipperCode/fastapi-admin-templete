from typing import Generator

from sqlalchemy.orm import sessionmaker

from app.db.session import SessionLocal


# async def async_session():
#
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#         except Exception:
#             session.rollback()
#             raise


def create_session() -> SessionLocal:
    with SessionLocal() as session:
        yield session
