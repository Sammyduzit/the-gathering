from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.auth_dependencies import get_current_active_user, get_current_admin_user
from app.models.room import Room
from app.models.user import User
from app.schemas.room_schemas import RoomResponse, RoomCreate

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)

@router.get("/", response_model=list[RoomResponse])
async def get_all_rooms(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)
                        ):
    """
    Get all active rooms.
    :param db: Database session
    :param current_user: Current authenticated user
    :return: List of active rooms
    """
    select_active_rooms = select(Room).where(Room.is_active.is_(True))

    result = db.execute(select_active_rooms)
    rooms = result.scalars().all()
    return rooms




@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(room_data: RoomCreate,
                      db: Session = Depends(get_db),
                      current_admin: User = Depends(get_current_admin_user)
                      ):
    """
    Create a new room.
    :param room_data: Room creation data
    :param db: Database session
    :param current_admin: Current authenticated admin
    :return: Created room object
    """
    existing_room_query = select(Room).where(Room.name == room_data.name)
    result = db.execute(existing_room_query)
    existing_room = result.scalar_one_or_none()

    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room with name '{room_data.name}' already exists"
        )

    new_room = Room(
        name=room_data.name,
        description=room_data.description,
        max_users = room_data.max_users
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(room_id: int,
                      room_data: RoomCreate,
                      db: Session = Depends(get_db),
                      current_admin: User = Depends(get_current_admin_user)
                      ):
    """
    Update existing room data.
    :param room_id: ID of the room to update
    :param room_data: Room data to update
    :param db: Database session
    :param current_admin: Current authenticated admin
    :return: Updated room object
    """
    select_room = select(Room).where(and_(Room.id == room_id, Room.is_active.is_(True)))
    result = db.execute(select_room)

    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )

    if room_data.name != room.name:
        existing_name_query = select(Room).where(Room.name == room_data.name)
        result = db.execute(existing_name_query)
        existing_room = result.scalar_one_or_none()

        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room with name '{room_data.name}' already exists"
            )

    room.name = room_data.name
    room.description = room_data.description
    room.max_users = room_data.max_users

    db.commit()
    db.refresh(room)

    return room


@router.delete("/{room_id}", response_model=RoomResponse)
async def delete_room(room_id: int,
                      db: Session = Depends(get_db),
                      current_admin: User = Depends(get_current_admin_user)
                      ):
    """
    Delete room by ID.
    :param room_id: ID of room to delete
    :param db: Database session
    :param current_admin: Current authenticated admin
    :return: Deleted room object
    """
    select_room = select(Room).where(and_(Room.id == room_id, Room.is_active.is_(True)))
    result = db.execute(select_room)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )

    room.is_active = False
    db.commit()

    return room

@router.get("/count")
async def get_room_count(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)
                         ):
    """
    Get count of active rooms.
    :param db: Database session
    :param current_user: Current authenticated user
    :return: Dictionary with room count
    """
    select_count = select(Room).where(Room.is_active.is_(True))
    result = db.execute(select_count)
    rooms = result.scalars().all()

    return {
        "active rooms" : len(rooms),
        "message": f"Found {len(rooms)} active rooms"
    }


@router.get("/health")
async def rooms_health():
    """Health check"""
    return {"status": "rooms endpoint working"}


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room_by_id(room_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)
                         ):
    """
    Get single room by ID.
    :param room_id: ID of room
    :param db: Database Session
    :param current_user: Current authenticated user
    :return: Room object
    """
    select_room = select(Room).where(and_(Room.id == room_id, Room.is_active.is_(True)))
    result = db.execute(select_room)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )

    return room























