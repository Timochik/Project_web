import asyncio
from src.database.models import Post, User, UserRole, Comments
from src.services.auth import auth_service


def test_post_comment_image_not_found(client, comment, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/comments",
        headers=headers,
        json=comment,
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Image not found"


def test_post_comment(client, comment, get_token, session):
    test_image = Post(
        description="test_description",
        image_url="http://test_url.com",
        author_id=1
    )
    session.add(test_image)
    session.commit()

    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/comments",
        headers=headers,
        json=comment,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["image_id"] == comment.get("image_id")
    assert data["text"] == comment.get("text")
    assert "id" in data
    assert "created_at" in data
    assert data["updated_at"] is None


def test_change_comment(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "comment_id": 1,
        "new_text": "New_text"
    }
    response = client.put(
        "/api/comments",
        headers=headers,
        json=body,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == body.get("comment_id")
    assert data["text"] == body.get("new_text")
    assert "created_at" in data
    assert data["updated_at"] is not None


def test_change_comment_not_found(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "comment_id": 2,
        "new_text": "New_text"
    }
    response = client.put(
        "/api/comments",
        headers=headers,
        json=body,
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Comment not found"


def test_change_comment_access_denied(client, session):
    second_test_user = User(
        username="username",
        email="email@example.com",
        password="password",
        role=UserRole.user
    )
    session.add(second_test_user)
    session.commit()

    token = asyncio.run(
        auth_service.create_access_token(
            data={"sub": second_test_user.email}
        )
    )
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "comment_id": 1,
        "new_text": "New_text_from_invalid_user"
    }
    response = client.put(
        "/api/comments",
        headers=headers,
        json=body,
    )
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Access denied"


def test_get_comment(client, session):
    comment_id = 1
    current_comment: Comments = session.query(Comments).filter(
        Comments.id == comment_id
    ).first()
    response = client.get(f"/api/comments/{comment_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == current_comment.id
    assert data["text"] == current_comment.text
    assert data["created_at"] == current_comment.created_at.isoformat()
    assert data["updated_at"] == current_comment.updated_at.isoformat()
    assert data["image_id"] == current_comment.image_id
    assert data["user_id"] == current_comment.user_id


def test_get_comment_not_found(client):
    comment_id = 2
    response = client.get(f"/api/comments/{comment_id}")
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Comment not found"


def test_get_comment_by_image(client, session):
    image_id = 1
    comments = session.query(Comments).filter(
        Comments.image_id == image_id
    ).all()
    response = client.get(f"/api/comments/by-image/{image_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == len(comments)


def test_get_comment_by_image_not_found(client):
    image_id = 2
    response = client.get(f"/api/comments/by-image/{image_id}")
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Image not found"


def test_get_comments_by_user(client, session, user):
    current_user = session.query(User).filter(
        User.email == user["email"]
    ).first()
    comments = session.query(Comments).filter(
        Comments.user_id == current_user.id
    ).all()
    response = client.get(f"/api/comments/by-user/{current_user.id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == len(comments)


def test_get_comments_by_user_not_found(client):
    user_id = 3
    response = client.get(f"/api/comments/by-user/{user_id}")
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "User not found"


def test_delete_comment_access_denied(client, get_token):
    comment_id = 1
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(
        f"/api/comments/{comment_id}",
        headers=headers
    )
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Access denied"


def test_delete_comment(client, get_token, session, user):
    comment_id = 1
    current_comment: Comments = session.query(Comments).filter(
        Comments.id == comment_id
    ).first()

    current_user = session.query(User).filter(
        User.email == user["email"]
    ).first()
    current_user.role = UserRole.moderator
    session.commit()

    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(
        f"/api/comments/{comment_id}",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == current_comment.id
    assert data["text"] == current_comment.text
    assert data["created_at"] == current_comment.created_at.isoformat()
    assert data["updated_at"] == current_comment.updated_at.isoformat()
    assert data["image_id"] == current_comment.image_id
    assert data["user_id"] == current_comment.user_id


def test_delete_comment_not_found(client, get_token, session, user):
    comment_id = 1
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(
        f"/api/comments/{comment_id}",
        headers=headers
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Comment not found"
