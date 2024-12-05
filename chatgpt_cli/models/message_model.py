from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import Base


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat"}

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat.chats.id"))
    sender = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    model = Column(String, nullable=True)

    chat = relationship("Chat", back_populates="messages")
