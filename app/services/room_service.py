from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from app.models.room import Room
from app.models.user import User


def get_room_or_404(db: Session, room_id: int) -> Room:
    """
    Get active room by ID or raise 404.
    :param db: Database session
    :param room_id: Room ID to fetch
    :return: Room object
    """
    room_query = select(Room).where(and_(Room.id == room_id, Room.is_active.is_(True)))
    result = db.execute(room_query)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )
    return room



def get_room_user_count(db: Session, room_id: int) -> int:
    """
    Get count of users currently in room.
    :param db: Database session
    :param room_id: Room ID
    :return: Number of users in room
    """
    user_count_query = select(func.count(User.id)).where(User.current_room_id == room_id)
    result = db.execute(user_count_query)
    user_count = result.scalar()

    return user_count


def validate_room_capacity(room: Room, current_count: int) -> None:
    """
    Check if room has capacity for additional user.
    :param room: Room object
    :param current_count: Current number if users in room
    :return: None
    """
    if room.max_users and current_count >= room.max_users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Room '{room.name}' is full (max {room.max_users} users)"
        )


def validate_room_name_unique(db: Session, name: str, exclude_room_id: int | None = None):
    """
    Check if room name is unique.
    :param db: Database session
    :param name: Room name to check
    :param exclude_room_id: Room ID to exclude from check
    :return: None
    """
    room_query = select(Room).where(
        and_(
        Room.name == name,
        Room.is_active.is_(True)
        )
    )

    if exclude_room_id:
        room_query = room_query.where(Room.id != exclude_room_id)

    result = db.execute(room_query)
    existing_room = result.scalar_one_or_none()

    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Room name '{name}' already exists"
        )
