from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    chat_id: int
    sender: str
    content: str


class MessageRead(BaseModel):
    id: int
    chat_id: int
    sender: str
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True
