from typing import Optional

from chatgpt_cli.models.user_model import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    async def create_user(self, session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def get_user_by_username(
        self, session: AsyncSession, username: str
    ) -> Optional[User]:
        statement = await session.execute(select(User).where(User.username == username))
        user = statement.scalar_one_or_none()
        return user
