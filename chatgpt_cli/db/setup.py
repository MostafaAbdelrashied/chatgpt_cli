from sqlalchemy.sql import text

from chatgpt_cli.db.session import engine
from chatgpt_cli.models.base_model import Base


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS chat"))
        await conn.run_sync(Base.metadata.create_all)
