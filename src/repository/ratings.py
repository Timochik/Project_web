from sqlalchemy.orm import Session
from src.database.models import Rating, User, Post, UserRole
from src.schemas import RatingCreate
from fastapi import HTTPException, status


async def create_rating(db: Session, user: User, image: Post, rating_value: int) -> Rating:
    """
    Create a new rating for an image by a user.

    Args:
        db (Session): Database session.
        user (User): The user creating the rating.
        image (Post): The image being rated.
        rating_value (int): The value of the rating.

    Returns:
        Rating: The created rating.
    """
    existing_rating = db.query(Rating).filter(Rating.user_id == user.id, Rating.image_id == image.id).first()
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already rated this image")

    if image.author_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot rate your own image")

    new_rating = Rating(user_id=user.id, image_id=image.id, rating=rating_value)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


async def get_ratings(db: Session, image_id: int):
    """
    Get all ratings for a specific image.

    Args:
        db (Session): Database session.
        image_id (int): ID of the image.

    Returns:
        List[Rating]: List of ratings for the image.
    """
    return db.query(Rating).filter(Rating.image_id == image_id).all()


async def delete_rating(db: Session, rating_id: int, current_user: User):
    """
    Delete a rating by ID.

    Args:
        db (Session): Database session.
        rating_id (int): ID of the rating to delete.
        current_user (User): The current user performing the delete action.

    Returns:
        dict: Confirmation message.
    """
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    if current_user.role not in [UserRole.admin, UserRole.moderator] and rating.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    db.delete(rating)
    db.commit()
    return {"message": "Rating deleted successfully"}


def calculate_average_rating(db: Session, image_id: int) -> float:
    """
    Calculate the average rating for a specific image.

    Args:
        db (Session): Database session.
        image_id (int): ID of the image.

    Returns:
        float: The average rating for the image.
    """
    ratings = db.query(Rating).filter(Rating.image_id == image_id).all()

    if not ratings:
        return 0.0

    total_score = sum(rating.rating for rating in ratings)
    average_rating = total_score / len(ratings)
    return average_rating
