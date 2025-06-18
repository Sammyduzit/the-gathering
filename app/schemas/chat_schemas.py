from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class MessageCreate(BaseModel):
    """
    Schema for creating a room message.
    """
    content: str = Field(min_length=1, max_length=500, description="Message content")


class MessageResponse(BaseModel):
    """
    Basic message response.
    """
    id : int
    sender_id: int
    sender_username: str
    content: str
    sent_at: datetime
    room_id: int

    model_config = ConfigDict(from_attributes=True)

