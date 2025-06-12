from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoomResponse(BaseModel):
    "room API Response"
    id: int
    name: str
    description: Optional[str] = None
    max_users: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

