import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskdb"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    @property
    def sync_database_url(self) -> str:
        """Sync URL for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "+psycopg").replace(
            "+aiosqlite", ""
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
