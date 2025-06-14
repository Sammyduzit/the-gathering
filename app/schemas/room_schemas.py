from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class RoomResponse(BaseModel):
    """
    Schema for room responses.
    """
    id: int
    name: str
    description: str | None = None
    max_users: int | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomCreate(BaseModel):
    """
    Schema for creating a new room.
    Input validation for POST requests.
    """
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    max_users: int | None = Field(None, ge=1, le=1000)

