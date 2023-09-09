from sqlalchemy import NullPool, QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_app_settings
from app.settings.app_env_types import AppEnvTypes

settings = get_app_settings()
SQLALCHEMY_DATABASE_URL = f"{settings.db_engine}://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    future=True,
    echo=False,
    poolclass=NullPool if settings.app_env == AppEnvTypes.TEST else QueuePool,
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
