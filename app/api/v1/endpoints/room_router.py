from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.room import Room
from app.schemas.room_schemas import RoomResponse

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)

@router.get("/", response_model=List[RoomResponse])
async def get_all_rooms(db: Session = Depends(get_db)):
    """Get all rooms"""
    rooms = db.query(Room).all()
    return rooms

@router.get("/health")
async def rooms_health():
    """Health check"""
    return {"status": "rooms endpoint working"}