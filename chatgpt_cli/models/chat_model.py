from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import Base


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = {"schema": "chat"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("chat.users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat")
