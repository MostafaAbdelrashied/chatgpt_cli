from typing import List

from sqlalchemy import select

from chatgpt_cli.db.session import get_session
from chatgpt_cli.models.chat_model import Chat


class ChatRepository:
    async def create_chat(self, chat: Chat) -> Chat:
        async with get_session() as session:
            session.add(chat)
            await session.commit()
            await session.refresh(chat)
            return chat

    async def get_chats_by_user(self, user_id: int) -> List[Chat]:
        async with get_session() as session:
            statement = await session.execute(
                select(Chat).where(Chat.user_id == user_id)
            )
            return statement.scalars().all()
