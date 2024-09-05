from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import config

SQLALCHEMY_DB_URL = f"postgresql+asyncpg://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/internetshop"

engine = create_async_engine(SQLALCHEMY_DB_URL)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session():
    async with async_session() as session:
        yield session
