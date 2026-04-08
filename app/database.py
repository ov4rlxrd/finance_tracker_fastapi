from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from typing import Annotated
from fastapi import Depends
from config import settings


# 2. Создание движка
engine = create_async_engine(settings.database_url)

# 3. Создание фабрики сессий
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass

async def get_db():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]