from typing import Optional

from sqlalchemy import select

from chatgpt_cli.db.session import get_session
from chatgpt_cli.models.user_model import User


class UserRepository:
    async def create_user(self, user: User) -> User:
        async with get_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        async with get_session() as session:
            statement = await session.execute(
                select(User).where(User.username == username)
            )
            user = statement.scalar_one_or_none()
            return user
