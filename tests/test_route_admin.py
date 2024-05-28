from src.database.models import User, UserRole


def test_change_user_role_forbidden(client, session, user, get_token):
    current_user = session.query(User).filter(
        User.email == user["email"]
    ).first()
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/admin/change-role",
        json={
            "user_id": current_user.id,
            "new_role": UserRole.moderator
        },
        headers=headers
    )
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Not enough permissions"


def test_change_user_role(client, session, user, second_user, get_token):
    current_user = session.query(User).filter(
        User.email == user["email"]
    ).first()
    current_user.role = UserRole.admin

    second_test_user = User(
        username=second_user["username"],
        email=second_user["email"],
        password=second_user["password"],
        role=UserRole.user
    )
    session.add(second_test_user)
    session.commit()

    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/admin/change-role",
        json={
            "user_id": second_test_user.id,
            "new_role": UserRole.moderator
        },
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["role"] == UserRole.moderator


def test_change_user_role_not_found(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/admin/change-role",
        json={
            "user_id": 3,
            "new_role": UserRole.moderator
        },
        headers=headers
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "User not found"


def test_ban_user_forbidden(client, session, user, get_token):
    current_user = session.query(User).filter(
        User.email == user["email"]
    ).first()
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/api/admin/ban/{current_user.id}",
        headers=headers
    )
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Not enough permissions"


def test_ban_user_not_found(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/admin/ban/3",
        headers=headers
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "User not found"


def test_ban_user(client, session, second_user, get_token):
    second_test_user = session.query(User).filter(
        User.email == second_user["email"]
    ).first()
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/api/admin/ban/{second_test_user.id}",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    banned_user_id = data["id"]
    banned_user = session.query(User).filter(
        User.id == banned_user_id
    ).first()
    assert banned_user.is_active == False


def test_unban_user_not_found(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/admin/unban/3",
        headers=headers
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "User not found"
    

def test_unban_user(client, session, second_user, get_token):
    second_test_user = session.query(User).filter(
        User.email == second_user["email"]
    ).first()
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/api/admin/unban/{second_test_user.id}",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    banned_user_id = data["id"]
    banned_user = session.query(User).filter(
        User.id == banned_user_id
    ).first()
    assert banned_user.is_active == True
