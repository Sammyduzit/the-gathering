from app.core.database import Base, engine, SessionLocal, drop_tables, create_tables
from app.models.user import User
from app.models.room import Room

print("Testing User - Room connection: ...")

print("Cleaning database...")
drop_tables()
print("Create fresh tables...")
create_tables()

db = SessionLocal()

try:
    room = Room(
        name="TestRoom",
        description="Testing connection"
    )

    db.add(room)
    db.commit()
    db.refresh(room)
    print(f"Room created: {room}")

    user = User(
        email="test@test.com",
        username="tester",
        password_hash="123",
        current_room_id=room.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User created: {user}")
    print(f"User is in room: {user.current_room_id}")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
