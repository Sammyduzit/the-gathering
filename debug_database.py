from app.core.database import Base, engine, SessionLocal, drop_tables, create_tables
from app.models.user import User
from app.models.room import Room

print("🔍 Debug Database State...")

db = SessionLocal()

try:
    users = db.query(User).all()
    rooms = db.query(Room).all()
    print(f"Current Users in DB: {len(users)}")
    print(f"Current Rooms in DB: {len(rooms)}")

    for user in users:
        print(f"  User: {user}")
    for room in rooms:
        print(f"  Room: {room}")

except Exception as e:
    print(f"Error querying: {e}")
finally:
    db.close()

print("\n🗑️ Cleaning database...")
drop_tables()
print("✅ Database cleaned!")