import pytest
from sqlalchemy.orm import Session
from src.repository.ratings import create_rating, get_ratings, delete_rating, calculate_average_rating
from src.database.models import User, Post, Rating, UserRole
from fastapi import HTTPException


@pytest.fixture(scope="function")
def setup_data(session: Session):

    author = User(username="author", email="author@example.com", password="hashedpassword")
    session.add(author)
    session.commit()

    post = Post(description="Test Image", image_url="http://example.com/image.jpg", author_id=author.id)
    session.add(post)
    session.commit()

    user = User(username="testuser", email="test@example.com", password="hashedpassword")
    session.add(user)
    session.commit()

    yield user, post, author

    # Clean up after the test
    session.query(Rating).delete()
    session.query(Post).delete()
    session.query(User).delete()
    session.commit()


@pytest.mark.asyncio
async def test_create_rating(session: Session, setup_data):
    user, post, _ = setup_data
    rating_value = 5

    new_rating = await create_rating(session, user, post, rating_value)
    assert new_rating.rating == rating_value
    assert new_rating.user_id == user.id
    assert new_rating.image_id == post.id


@pytest.mark.asyncio
async def test_create_rating_existing(session: Session, setup_data):
    user, post, _ = setup_data
    rating_value = 5

    await create_rating(session, user, post, rating_value)

    with pytest.raises(HTTPException):
        await create_rating(session, user, post, rating_value)


@pytest.mark.asyncio
async def test_create_rating_own_image(session: Session, setup_data):
    user, post, author = setup_data
    rating_value = 5

    with pytest.raises(HTTPException):
        await create_rating(session, author, post, rating_value)


@pytest.mark.asyncio
async def test_get_ratings(session: Session, setup_data):
    user, post, _ = setup_data
    rating_value = 5

    await create_rating(session, user, post, rating_value)

    ratings = await get_ratings(session, post.id)
    assert len(ratings) == 1
    assert ratings[0].rating == rating_value


@pytest.mark.asyncio
async def test_delete_rating(session: Session, setup_data):
    user, post, _ = setup_data
    rating_value = 5

    new_rating = await create_rating(session, user, post, rating_value)

    response = await delete_rating(session, new_rating.id, user)
    assert response == {"message": "Rating deleted successfully"}


@pytest.mark.asyncio
async def test_calculate_average_rating(session: Session, setup_data):
    user, post, _ = setup_data
    rating_value = 5

    await create_rating(session, user, post, rating_value)

    average_rating = calculate_average_rating(session, post.id)
    assert average_rating == rating_value