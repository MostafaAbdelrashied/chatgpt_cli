from typing import List

from sqlalchemy import select
from chatgpt_cli.db.session import get_session

from chatgpt_cli.models.message_model import Message


class MessageRepository:
    async def create_message(self, message: Message) -> Message:
        async with get_session() as session:
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message
    
    async def get_messages_by_chat(self, chat_id: int) -> List[Message]:
        async with get_session() as session:
            statement = await session.execute(
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.timestamp)
            )
            return statement.scalars().all()