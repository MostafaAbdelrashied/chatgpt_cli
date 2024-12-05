from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatgpt_cli.models.chat_model import Chat


class ChatRepository:
    async def create_chat(self, session: AsyncSession, chat: Chat) -> Chat:
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat

    async def get_chats_by_user(
        self, session: AsyncSession, user_id: int
    ) -> List[Chat]:
        statement = await session.execute(select(Chat).where(Chat.user_id == user_id))
        return statement.scalars().all()

    async def get_chat_by_id(
        self, session: AsyncSession, chat_id: int
    ) -> Optional[Chat]:
        return await session.get(Chat, chat_id)
