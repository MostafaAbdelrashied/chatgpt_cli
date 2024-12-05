from typing import List

from chatgpt_cli.models.message_model import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class MessageRepository:
    async def create_message(self, session: AsyncSession, message: Message) -> Message:
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    async def get_messages_by_chat(
        self, session: AsyncSession, chat_id: int
    ) -> List[Message]:
        statement = await session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
        )
        return statement.scalars().all()
