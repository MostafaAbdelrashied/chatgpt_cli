from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat.id"))
    sender = Column(String)  # 'user' or 'assistant'
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")
