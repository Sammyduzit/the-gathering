from app.core.database import Base, engine
from app.models.user import User, UserStatus

print("Testing User Model: ...")

Base.metadata.create_all(bind=engine)
print("User table created. \n")

test_user = User(
    email="test@test.com",
    username="testuser",
    password_hash="hashed_password",
    status=UserStatus.AVAILABLE
)

print(f"User object created: {test_user}")