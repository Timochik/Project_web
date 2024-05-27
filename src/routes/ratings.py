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
    The rate_image function creates a new rating for an image by a user.
    
    :param rating: RatingCreate: Create a new rating
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A ratingresponse object
    :doc-author: Trelent
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
    The get_image_ratings function returns a list of ratings for a specific image.
    
    :param image_id: int: Specify the id of the image
    :param db: Session: Pass in the database session
    :param current_user: User: Get the current user
    :return: A list of ratingresponse objects
    :doc-author: Trelent
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
    The delete_image_rating function deletes a rating by ID.
    
    :param rating_id: int: Identify the rating to be deleted
    :param db: Session: Access the database
    :param current_user: User: Ensure that the user performing the action is logged in
    :return: A dict
    :doc-author: Trelent
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
    The get_average_rating function returns the average rating for an image.
    
    :param image_id: int: Specify the id of the image
    :param db: Session: Get the database session
    :param current_user: User: Get the current user making the request
    :return: The average rating for an image
    :doc-author: Trelent
    """
    average_rating = calculate_average_rating(db, image_id)
    return average_rating
