from src.database.models import Post


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
        description = "test_description",
        image_url = "http://test_url.com",
        author_id = 1
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

