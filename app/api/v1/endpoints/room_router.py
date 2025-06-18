from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from app.core.database import get_db
from app.core.auth_dependencies import get_current_active_user, get_current_admin_user
from app.models.room import Room
from app.models.user import User, UserStatus
from app.schemas.chat_schemas import MessageResponse, MessageCreate
from app.schemas.room_schemas import RoomResponse, RoomCreate
from app.schemas.room_user_schemas import (
    RoomJoinResponse,
    RoomLeaveResponse,
    RoomUsersListResponse,
    RoomUserResponse,
    UserStatusUpdate
)
from app.services.room_service import (
    get_room_or_404,
    get_room_user_count,
    validate_room_capacity,
    validate_room_name_unique,
    create_room_message
)


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
    validate_room_name_unique(db, room_data.name)

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
    room = get_room_or_404(db, room_id)

    if room_data.name != room.name:
        validate_room_name_unique(db, room_data.name, room_id)

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
    Soft delete room by ID.
    :param room_id: ID of room to delete
    :param db: Database session
    :param current_admin: Current authenticated admin
    :return: Deleted room object
    """
    room = get_room_or_404(db, room_id)

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
    room_count_query = select(func.count(Room.id)).where(Room.is_active.is_(True))
    result = db.execute(room_count_query)
    room_count = result.scalar()

    return {
        "active rooms" : room_count,
        "message": f"Found {room_count} active rooms"
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
    room = get_room_or_404(db, room_id)
    return room



@router.post("/{room_id}/join", response_model=RoomJoinResponse)
async def join_room(room_id: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)
                    ):
    """
    User joins room.
    :param room_id: ID of room to join
    :param db: Database session
    :param current_user: Current authenticated user
    :return: Join confirmation with room info
    """
    room = get_room_or_404(db, room_id)

    current_user_count = get_room_user_count(db, room_id)

    validate_room_capacity(room, current_user_count)

    current_user.current_room_id = room_id
    current_user.status = UserStatus.AVAILABLE

    db.commit()
    db.refresh(current_user)

    final_user_count = get_room_user_count(db, room_id)

    return RoomJoinResponse(
        message=f"Successfully joined room '{room.name}'",
        room_id=room_id,
        room_name=room.name,
        user_count=final_user_count
    )


@router.post("/{room_id}/leave", response_model=RoomLeaveResponse)
async def leave_room(room_id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_active_user)
                     ):
    """
    User leaves room.
    :param room_id: ID of room to leave
    :param db: Database session
    :param current_user: Current authenticated user
    :return: Leave confirmation
    """
    room = get_room_or_404(db, room_id)

    if current_user.current_room_id != room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is not in room '{room.name}'"
        )

    current_user.current_room_id = None
    current_user.status = UserStatus.AWAY

    db.commit()

    return RoomLeaveResponse(
        message=f"Left room '{room.name}'",
        room_id=room_id,
        room_name=room.name
    )


@router.get("/{room_id}/users", response_model=RoomUsersListResponse)
async def get_room_users(room_id: int,
                         db:Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)
                         ):
    """
    Get list of users currently in a room.
    :param room_id: Room ID
    :param db: Database session
    :param current_user: Current authenticated user
    :return: List of users in room
    """

    room = get_room_or_404(db, room_id)

    users_query = select(User).where(and_(User.current_room_id == room.id,
                                          User.is_active.is_(True))
                                     ).order_by(User.username)

    result = db.execute(users_query)
    users = result.scalars().all()

    room_users = [
        RoomUserResponse(
            id=user.id,
            username= user.username,
            status=user.status.value,
            last_active=user.last_active
        )
        for user in users
    ]

    return RoomUsersListResponse(
        room_id=room_id,
        room_name=room.name,
        total_users=len(room_users),
        users=room_users
    )


@router.patch("/users/status", response_model=dict)
async  def update_user_status(status_update: UserStatusUpdate,
                              db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_active_user)
                              ):
    """
    Update current user status.
    :param status_update: New status data
    :param db: Database session
    :param current_user: Current authenticated user
    :return: Status update confirmation
    """
    current_user.status = status_update.status

    db.commit()

    return {
        "message": f"Status updated to '{status_update.status.value}'",
        "new_status": status_update.status.value,
        "user": current_user.username
    }


@router.post("/{room_id}/message", response_model=MessageResponse)
async def send_room_message(room_id: int,
                            message_data: MessageCreate = Body(...),
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_active_user),
                            ):
    """
    Send message to room, visible for every member.
    :param room_id: Target room ID
    :param message_data: Message content
    :param db: Database session
    :param current_user: Current authenticated user
    :return: Created message object
    """

    new_message = create_room_message(db, current_user.id, room_id, message_data.content)

    new_message.sender_username = current_user.username

    return new_message









