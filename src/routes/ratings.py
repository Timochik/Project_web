from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User, Post
from src.services.auth import auth_service
from src.schemas import RatingCreate, RatingResponse
from src.repository.ratings import create_rating, get_ratings, delete_rating, calculate_average_rating

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("/", response_model=RatingResponse, summary="Create a new rating")
async def rate_image(
        rating: RatingCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new rating for an image by a user.

    Args:
        rating (RatingCreate): The data for creating a new rating.
        db (Session): Database session.
        current_user (User): The current user creating the rating.

    Returns:
        RatingResponse: The created rating.
    """
    image = db.query(Post).filter(Post.id == rating.image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    new_rating = await create_rating(db, current_user, image, rating.rating)
    return new_rating


@router.get("/{image_id}", response_model=List[RatingResponse], summary="Get all ratings for an image")
async def get_image_ratings(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get all ratings for a specific image.

    Args:
        image_id (int): ID of the image.
        db (Session): Database session.
        current_user (User): The current user.

    Returns:
        List[RatingResponse]: List of ratings for the image.
    """
    ratings = await get_ratings(db, image_id)
    return ratings


@router.delete("/{rating_id}", response_model=dict, summary="Delete a rating by ID")
async def delete_image_rating(
        rating_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Delete a rating by ID.

    Args:
        rating_id (int): ID of the rating to delete.
        db (Session): Database session.
        current_user (User): The current user performing the delete action.

    Returns:
        dict: Confirmation message.
    """
    response = await delete_rating(db, rating_id, current_user)
    return response


@router.get("/{image_id}/average", response_model=float)
async def get_average_rating(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get the average rating for an image.

    Args:
        image_id (int): ID of the image.
        db (Session): Database session.
        current_user (User): The current user making the request.

    Returns:
        float: The average rating for the image.
    """
    average_rating = calculate_average_rating(db, image_id)
    return average_rating