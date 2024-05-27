from fastapi import Depends, File, HTTPException, UploadFile, APIRouter, status
from sqlalchemy.orm import Session
from typing import List

from src.schemas import (
    ImageResponce,
    CropImageRequest,
    RoundCornersImageRequest,
    EffectImageRequest
)
from src.database.models import User
from src.database.db import get_db
from src.repository import images as repository_images
from src.services.auth import auth_service, check_is_admin_or_moderator
from src.utils.image_utils import transform_image


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
    for i in hashtags:
        tags_list = i.split(',')
    if len(tags_list) > 5:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Limit of 5 tags")
    return await repository_images.create_images_post(description, tags_list, current_user, db,  file)

@router.get("/get_image")
async def get_image(
    image_id : int,
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_image function returns a single image from the database.
        The function takes an integer as its only argument, which is the id of the image to be returned.
        The function returns a JSON object containing all information about that particular image.
    
    :param image_id : int: Get the image with that id from the database
    :param user_id: int: Get the image of another user
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A single image from the database
    :doc-author: Trelent
    """
    if not user_id:
        return await repository_images.get_image(image_id, current_user.id, db)
    return await repository_images.get_image(image_id, user_id, db)

@router.get("/get_images")
async def get_images(
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_images function returns a list of images that the current user has uploaded.
                
            
            
        
    
    :param user_id: int: Get the images for a specific user
    :param db: Session: Pass the database connection to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A list of images that the current user has uploaded
    :doc-author: Trelent
    """
    if not user_id:
        return await repository_images.get_images(user_id=current_user.id, db=db)
    return await repository_images.get_images(user_id=user_id, db=db)

@router.delete("/delete_image")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    """
    The delete_image function deletes an image from the database.
            
        
        
    
    :param image_id: int: Identify the image to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the auth_service
    :return: A dictionary with the following keys:
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
    
    :param image_id: int: Identify which image is being deleted
    :param new_description: str: Update the description of an image
    :param db: Session: Pass the database session to the repository function
    :param current_user: User: Get the current user
    :return: A new image
    :doc-author: Trelent
    """
    return await repository_images.put_image(image_id, new_description, current_user, db)


@router.post(
    "/transformation/crop",
    response_model=ImageResponce
)
async def crop_image_view(
    body: CropImageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The crop_image_view function that allows users to crop an image.
    
    :param body: CropImageRequest: Parse the request body
    :param db: Session: Access the database
    :param current_user: User: Get the user who is currently logged in
    :return: A cropped image
    :doc-author: Trelent
    """
    transform_params = {
        "height": body.height,
        "width": body.width,
        "crop": "crop"
    }
    return await transform_image(
        image_id=body.image_id,
        transform_params=transform_params,
        description=body.description,
        db=db,
        current_user=current_user
    )


@router.post(
    "/transformation/roundcorners",
    response_model=ImageResponce
)
async def round_corners(
    body: RoundCornersImageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The round_corners function takes an image ID and a radius,
    and returns the original image with rounded corners.
    
    
    :param body: RoundCornersImageRequest: Parse the request body
    :param db: Session: Access the database
    :param current_user: User: Get the user who is logged in
    :return: A response object that contains the transformed image
    :doc-author: Trelent
    """
    transform_params = {"radius": body.radius}
    return await transform_image(
        image_id=body.image_id,
        transform_params=transform_params,
        description=body.description,
        db=db,
        current_user=current_user
    )


@router.post(
    "/transformation/grayscale",
    response_model=ImageResponce
)
async def grayscale(
    body: EffectImageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The grayscale function 
    
    :param body: EffectImageRequest: Get the image_id and description from the request body
    :param db: Session: Get a database session
    :param current_user: User: Get the user who is logged in
    :return: A response object that contains the transformed image
    :doc-author: Trelent
    """
    transform_params = {"effect": "grayscale"}
    return await transform_image(
        image_id=body.image_id,
        transform_params=transform_params,
        description=body.description,
        db=db,
        current_user=current_user
    )


@router.post(
    "/transformation/sepia",
    response_model=ImageResponce
)
async def sepia(
    body: EffectImageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The sepia function takes an image_id and a description,
        then applies the sepia effect to the image.
    
    
    :param body: EffectImageRequest: Get the image_id and description from the request body
    :param db: Session: Get a database session
    :param current_user: User: Get the user who is logged in
    :return: A response object that contains the transformed image
    :doc-author: Trelent
    """
    transform_params = {"effect": "sepia"}
    return await transform_image(
        image_id=body.image_id,
        transform_params=transform_params,
        description=body.description,
        db=db,
        current_user=current_user
    )
