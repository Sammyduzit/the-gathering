from pydoc import describe

from app.core.database import Base, engine
from app.models.room import Room

print("Testing Room Model: ...")

Base.metadata.create_all(bind=engine)
print("Room table created")

test_room = Room(
    name = "general",
    description="Main chat room",
    max_users=50
)

print(f"Room object created: {test_room}")
