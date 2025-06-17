import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.room import Room
from app.core.auth_utils import hash_password



SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Create new database session for each test.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Test user registration data.
    """
    return {
        "email": "user@example.com",
        "username": "testuser",
        "password": "password123"
    }

@pytest.fixture
def test_admin_data():
    """
    Test admin registration data.
    """
    return {
        "email": "admin@example.com",
        "username": "testadmin",
        "password": "adminpass"
    }


@pytest.fixture
def test_room_data():
    """
    Test room creation data.
    """
    return {
        "name": "Test Room",
        "description": "A test room",
        "max_users": 5
    }


@pytest.fixture
def created_user(db_session, test_user_data):
    """Create a user in database."""
    user = User(
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def created_admin(db_session, test_admin_data):
    """Create an admin in database."""
    admin = User(
        email=test_admin_data["email"],
        username=test_admin_data["username"],
        password_hash=hash_password(test_admin_data["password"]),
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def created_room(db_session, test_room_data):
    """Create a room in database."""
    room = Room(
        name=test_room_data["name"],
        description=test_room_data["description"],
        max_users=test_room_data["max_users"],
    )

    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room


@pytest.fixture
def authenticated_user(client, test_user_data, created_user):
    """Return headers with JWT token for authenticated requests."""
    login_response = client.post("/api/v1/auth/login",
                                 json={
                                     "email": test_user_data["email"],
                                     "password": test_user_data["password"]
                                 })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def authenticated_admin(client, test_admin_data, created_admin):
    """Return headers with JWT token for authenticated requests."""
    login_response = client.post("/api/v1/auth/login",
                                 json={
                                     "email": test_admin_data["email"],
                                     "password": test_admin_data["password"]
                                 })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}