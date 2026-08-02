from collections.abc import AsyncGenerator

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


_engine: AsyncEngine | None = None
_factory: async_sessionmaker[AsyncSession] | None = None


def _prepare_database_url(raw_url: str) -> tuple[URL, dict[str, object]]:
    """
    Chuẩn hóa URL PostgreSQL cho SQLAlchemy asyncpg.

    - Bảo đảm sử dụng driver postgresql+asyncpg.
    - Chuyển sslmode thành tham số ssl của asyncpg.
    - Loại bỏ channel_binding vì asyncpg không nhận tham số này.
    """
    database_url = make_url(raw_url)

    if database_url.drivername in {
        "postgres",
        "postgresql",
        "postgresql+psycopg2",
    }:
        database_url = database_url.set(
            drivername="postgresql+asyncpg",
        )

    query = dict(database_url.query)

    # Neon thường cung cấp sslmode=require.
    # asyncpg sử dụng tham số ssl, không sử dụng sslmode.
    ssl_value = query.pop("sslmode", None)

    if ssl_value is None:
        ssl_value = query.pop("ssl", None)

    # asyncpg không hỗ trợ tham số channel_binding.
    query.pop("channel_binding", None)

    database_url = database_url.set(query=query)

    connect_args: dict[str, object] = {}

    if ssl_value:
        connect_args["ssl"] = ssl_value

    return database_url, connect_args


def get_engine() -> AsyncEngine:
    global _engine

    if _engine is None:
        database_url, connect_args = _prepare_database_url(
            str(settings.database_url)
        )

        _engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            connect_args=connect_args,
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _factory

    if _factory is None:
        _factory = async_sessionmaker(
            get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )

    return _factory


def AsyncSessionLocal() -> AsyncSession:
    return get_session_factory()()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session