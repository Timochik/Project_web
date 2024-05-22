from fastapi import Depends, File, UploadFile, APIRouter
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from src.database.models import User
from src.database.db import get_db
from src.repository import images as repository_images
from src.services.auth import auth_service
from src.routes.utils import apply_effect, round_corners, crop_image

router = APIRouter(prefix='/images', tags=["images"])

@router.post("/upload")
async def upload_file(description: str, hashtags: List[str], db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),   file: UploadFile = File(...)):
    """
    The upload_file function is used to upload a file to the server.
        The function takes in a description, hashtags, and an image file.
        It then creates an entry in the database for that image with all of its information.
    
    :param description: str: Get the description of the image
    :param hashtags: List[str]: Get the hashtags from the request body
    :param db: Session: Access the database
    :param current_user: User: Get the user who is currently logged in
    :param file: UploadFile: Upload the file to the server
    :return: A tuple of the info
    :doc-author: Trelent
    """
    return await repository_images.create_images_post(description, hashtags, current_user, db,  file)

@router.get("/get_image")
async def get_image(image_id : int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_image function returns a single image from the database.
        The function takes an integer as its only argument, which is the id of the image to be returned.
        The function returns a JSON object containing all information about that particular image.
    
    :param image_id : int: Get the image with that id from the database
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A json object, which contains the info
    :doc-author: Trelent
    """
    return await repository_images.get_image(image_id, current_user, db)

@router.get("/get_images")
async def get_images(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_images function returns a list of images that the current user has uploaded.
        
    
    :param db: Session: Pass the database connection to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A list of image objects
    :doc-author: Trelent
    """
    return await repository_images.get_images(current_user, db)

@router.delete("/delete_image")
async def delete_image(image_id: int , db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The delete_image function deletes an image from the database.
        
    
    :param image_id: int: Identify the image to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the auth_service
    :return: A dictionary
    :doc-author: Trelent
    """
    return await repository_images.del_image(image_id, db, current_user)


@router.put("/edit_description")
async def put_image(image_id: int , new_description: str, 
                       db: Session = Depends(get_db), 
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The put_image function updates the description of an image.
        The user must be logged in and own the image to update it.
    
    :param image_id: int: Identify which image is being updated
    :param new_description: str: Update the description of an image
    :param db: Session: Pass the database session to the repository function
    :param current_user: User: Get the current user
    :return: New image
    :doc-author: Trelent
    """
    return await repository_images.put_image(image_id, new_description, current_user, db)
    
@router.get("/images/crop")
async def crop_image_view(image_url: str, width: int, height: int, description: str, hashtags: List[str], db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),   file: UploadFile = File(...)):
   return await crop_image(
    image_url=image_url,
    width=width,
    height=height,
    description=description,
    hashtags=hashtags,
    current_user=current_user,
    db=db,
    file=file
)

@router.get("/images/effect")
async def apply_effect_view( image_url: str, effect: str, description: str, hashtags: List[str], db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),   file: UploadFile = File(...)):
    return await apply_effect(
    image_url=image_url,
    effect = effect,
    description=description,
    hashtags=hashtags,
    current_user=current_user,
    db=db,
    file=file
)

@router.get("/images/roundcorners")
async def round_corners(image_url: str, radius: int, description: str, hashtags: List[str], db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),   file: UploadFile = File(...)):
    return await round_corners(
    image_url=image_url,
    radius = radius,
    description=description,
    hashtags=hashtags,
    current_user=current_user,
    db=db,
    file=file
)