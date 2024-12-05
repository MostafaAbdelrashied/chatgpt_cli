from datetime import datetime
from typing import List

from chatgpt_cli.schemas.message_schema import MessageRead
from pydantic import BaseModel


class ChatCreate(BaseModel):
    user_id: int


class ChatRead(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    messages: List[MessageRead] = []

    class Config:
        orm_mode = True
