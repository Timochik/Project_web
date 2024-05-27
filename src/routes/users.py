from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        The function takes in a parameter of the current_user, which is obtained from auth_service.get_current_user().
        This function will return an error if there is no logged in user.
    
    :param current_user: User: Get the current user
    :return: The current user's information
    :doc-author: Trelent
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function takes in a file, current_user and db as parameters.
    The function then uploads the file to cloudinary using the username of the user as its public id.
    It then builds a url for that image with specific dimensions and crops it to fill those dimensions. 
    Finally, it updates the avatar field in our database with this new url.
    
    :param file: UploadFile: Get the file from the request body
    :param current_user: User: Get the current user's email address
    :param db: Session: Access the database
    :return: The updated user object
    :doc-author: Trelent
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    
    r = cloudinary.uploader.upload(file.file, public_id=f'contacts/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'contacts/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


@router.get("/{username}", response_model=UserDb)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    The get_user_by_username function is used to get a user profile by unique username.
        
    
    :param username: str: Specify the username of the user to be retrieved
    :param db: Session: Pass the database session to the function
    :return: A userdb object
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=UserDb)
async def update_my_profile(user_update: UserUpdate, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_my_profile function allows the current user to update their own profile information.
    
    :param user_update: UserUpdate: Get the new user data
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current logged in user
    :return: The updated user object
    :doc-author: Trelent
    """
    updated_user = await repository_users.update_user(current_user.id, user_update, db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user