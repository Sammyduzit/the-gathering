import pytest
from fastapi import status

from tests.conftest import client


class TestAuthentication:
    """Core authentication."""

    def test_register_and_login_flow(self, client, test_user_data):
        """Test complete registration → login flow."""
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        print("Response JSON:", register_response.json())

        user_data = register_response.json()
        assert user_data["avatar_url"] is not None
        assert test_user_data["username"].lower() in user_data["avatar_url"]

        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert login_response.status_code == status.HTTP_200_OK
        assert "access_token" in login_response.json()

    def test_protected_endpoint_requires_auth(self, client):
        """Test protected endpoints require authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRoomBasics:
    """Core room functionality."""

    def test_admin_can_create_room(self, client, authenticated_admin, test_room_data):
        """Test admin room creation."""
        response = client.post("/api/v1/rooms/", json=test_room_data, headers=authenticated_admin)
        assert response.status_code == status.HTTP_201_CREATED

    def test_user_cannot_create_room(self, client, authenticated_user, test_room_data):
        """Test regular user cannot create rooms."""
        response = client.post("/api/v1/rooms/", json=test_room_data, headers=authenticated_user)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserRoomInteraction:
    """Core user-room interaction functionality."""

    def test_user_can_join_and_leave_room(self, client, authenticated_user, created_room):
        """Test complete join → leave flow."""
        join_response = client.post(f"/api/v1/rooms/{created_room.id}/join", headers=authenticated_user)
        assert join_response.status_code == status.HTTP_200_OK
        assert join_response.json()["user_count"] == 1

        leave_response = client.post(f"/api/v1/rooms/{created_room.id}/leave", headers=authenticated_user)
        assert leave_response.status_code == status.HTTP_200_OK

        users_response = client.get(f"/api/v1/rooms/{created_room.id}/users", headers=authenticated_user)
        assert users_response.json()["total_users"] == 0


class TestIntegration:
    """One complete user journey."""

    def test_complete_user_journey(self, client, test_user_data, test_room_data, db_session):
        """Test: Admin DB creation → Admin login → Admin creates room
        → User register → User login → User joins → User updates status."""
        from app.models.user import User
        from app.core.auth_utils import hash_password

        admin = User(
            email="admin@test.com",
            username="admin",
            password_hash=hash_password("adminpass"),
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()

        admin_login = client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "adminpass"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        room_response = client.post("/api/v1/rooms/", json=test_room_data, headers=admin_headers)
        room_id = room_response.json()["id"]

        # User part
        client.post("/api/v1/auth/register", json=test_user_data)

        user_login = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        user_headers = {"Authorization": f"Bearer {user_login.json()['access_token']}"}

        join_response = client.post(f"/api/v1/rooms/{room_id}/join", headers=user_headers)
        assert join_response.status_code == status.HTTP_200_OK

        status_response = client.patch("/api/v1/rooms/users/status",
                                       json={"status": "busy"},
                                       headers=user_headers)
        assert status_response.status_code == status.HTTP_200_OK