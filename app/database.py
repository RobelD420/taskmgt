from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine #Async Session with DB
from sqlalchemy.orm import DeclarativeBase #The ORM Base class

from app.config import get_settings #Settings for the database

settings = get_settings() #Gets the settings for the database without hardcoidng url

#Creates the engine for the database
engine = create_async_engine(settings.database_url, echo=False) #echo=False to not print the SQL queries every time

# Session maker for the database (expire_on_commit=False to not expire the session after the commit)
async_session = async_sessionmaker(engine, expire_on_commit=False)

#Base class for the database
class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
