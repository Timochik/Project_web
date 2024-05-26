from src.database.models import Post


def test_crop_image_view(client, session, get_token, mock_get_qr_code_by_url):
    test_image = Post(
        description="test_description",
        image_url="https://res.cloudinary.com/abcdefghi/image/upload/v1234567890/project_name/a96e4ceb-54de-4e37-9520-0d0d3a3a31a6",
        author_id=1
    )
    session.add(test_image)
    session.commit()

    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    transformation = {
        "image_id": 1,
        "width": 640,
        "height": 480,
        "description": "description"
    }

    response = client.post(
        "/api/images/transformation/crop",
        headers=headers,
        json=transformation
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["description"] == transformation["description"]
    assert "image_url" in data
    assert "author_id" in data
    assert "qr_code_url" in data
    assert "created_dt" in data


def test_round_corners(client, get_token, mock_get_qr_code_by_url):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    transformation = {
        "image_id": 1,
        "radius": 100,
        "description": "description"
    }

    response = client.post(
        "/api/images/transformation/roundcorners",
        headers=headers,
        json=transformation
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["description"] == transformation["description"]
    assert "image_url" in data
    assert "author_id" in data
    assert "qr_code_url" in data
    assert "created_dt" in data


def test_grayscale(client, get_token, mock_get_qr_code_by_url):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    transformation = {
        "image_id": 1,
        "description": "description"
    }

    response = client.post(
        "/api/images/transformation/grayscale",
        headers=headers,
        json=transformation
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["description"] == transformation["description"]
    assert "image_url" in data
    assert "author_id" in data
    assert "qr_code_url" in data
    assert "created_dt" in data


def test_sepia(client, get_token, mock_get_qr_code_by_url):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    transformation = {
        "image_id": 1,
        "description": "description"
    }

    response = client.post(
        "/api/images/transformation/sepia",
        headers=headers,
        json=transformation
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["description"] == transformation["description"]
    assert "image_url" in data
    assert "author_id" in data
    assert "qr_code_url" in data
    assert "created_dt" in data
