from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Rating, User, Post, UserRole


async def create_rating(db: Session, user: User, image: Post, rating_value: int) -> Rating:
    """
    The create_rating function creates a new rating for an image by a user.
    
    :param db: Session: Access the database
    :param user: User: Get the user that is creating the rating
    :param image: Post: Pass in the image being rated
    :param rating_value: int: Pass in the value of the rating
    :return: A rating object
    :doc-author: Trelent
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
    The get_ratings function returns a list of ratings for a specific image.
    
    :param db: Session: Pass the database session to the function
    :param image_id: int: Filter the database query
    :return: A list of rating objects
    :doc-author: Trelent
    """
    return db.query(Rating).filter(Rating.image_id == image_id).all()


async def delete_rating(db: Session, rating_id: int, current_user: User):
    """
    The delete_rating function deletes a rating by ID.
    
    :param db: Session: Pass the database session to the function
    :param rating_id: int: Get the rating that is to be updated
    :param current_user: User: Ensure that only the user who created the rating can delete it
    :return: A dictionary with a message key and the value &quot;rating deleted successfully&quot;
    :doc-author: Trelent
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
    The calculate_average_rating function calculates the average rating for a specific image.
    
    :param db: Session: Pass in the database session
    :param image_id: int: Specify the image id
    :return: The average rating for a specific image
    :doc-author: Trelent
    """
    ratings = db.query(Rating).filter(Rating.image_id == image_id).all()

    if not ratings:
        return 0.0

    total_score = sum(rating.rating for rating in ratings)
    average_rating = total_score / len(ratings)
    return average_rating
