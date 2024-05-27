import asyncio
from unittest.mock import MagicMock, patch, mock_open
from unittest import mock
from src.database.models import Post, User, UserRole, Comments
from src.schemas import UserUpdate
from src.services.auth import auth_service


def test_read_users_me(client, user, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/users/me",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert "created_at" in data
    assert "avatar" in data


def test_update_avatar_user(
    client,
    get_token,
    mock_cloudinary_uploader,
    mock_cloudinary_build_url
):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    with patch(
        "builtins.open",
        side_effect=mock_open(read_data="test")
    ):
        with open("mock_file") as mock_file:

            response = client.patch(
                "/api/users/avatar",
                headers=headers,
                files={"file": mock_file}
            )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["avatar"] == "avatar_url"


def test_get_user_by_username(client, user):
    username = user["username"]
    response = client.get(
        f"/api/users/{username}"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert "created_at" in data
    assert "avatar" in data


def test_get_user_by_username_not_found(client):
    username = "wrong_user_name"
    response = client.get(
        f"/api/users/{username}"
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_my_profile(client, get_token, mock_update_user):
    user = {
        "username": "new_username",
        "email": "new.email@example.com",
        "avatar": "new_avatar_url"
    }
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/users/me",
        json=user,
        headers=headers
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_my_profile_not_found(client, get_token):
    user = {
        "username": "new_username",
        "email": "new.email@example.com",
        "avatar": "new_avatar_url"
    }
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/users/me",
        json=user,
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert "created_at" in data
    assert "avatar" in data
