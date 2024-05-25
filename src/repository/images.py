from typing import List
import uuid
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.database.models import Post, User
from src.utils.qr_code import get_qr_code_by_url
from src.repository.tags import get_or_create_tag
from src.conf.config import settings
from sqlalchemy import and_

import cloudinary
import cloudinary.uploader

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

async def create_images_post(description: str, hashtags: List[str], user: User, db: Session, file: UploadFile)-> Post: 
    """
    The create_images_post function creates a new post in the database.
        Args:
            description (str): The description of the image.
            hashtags (List[str]): A list of hashtags to be associated with this post. 
                Each hashtag should be separated by a comma, and no spaces are allowed between commas or words in the hashtag itself.
    
    :param description: str: Get the description of the image from the request body
    :param hashtags: List[str]: Pass the list of hashtags that are in the request body
    :param user: User: Get the user id from the database
    :param db: Session: Pass the database session to the function
    :param file: UploadFile: Upload the file to cloudinary and get the url
    :return: A post object
    :doc-author: Trelent
    """
    dbtags =[]
    for i in hashtags:
        tags_list = i.split(',')
    for tag in tags_list:
        dbtag = await get_or_create_tag(db, tag)
        dbtags.append(dbtag)

    public_id = f'{settings.cloudinary_folder_name}/{uuid.uuid4()}'
    result = cloudinary.uploader.upload(file.file, public_id=public_id)
    url = result['secure_url']
    qr_url = await get_qr_code_by_url(url)    
    images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=dbtags)
    db.add(images)
    db.commit()
    db.refresh(images)
    return images
    

async def get_images(current_user: User, db: Session):
    """
    The get_images function returns all images that the current user has uploaded.
        
    
    :param current_user: User: Get the current user's id
    :param db: Session: Access the database
    :return: A list of post objects
    :doc-author: Trelent
    """
    return db.query(Post).filter(Post.author_id == str(current_user.id)).all()

async def get_image(image_id : int, current_user: User, db: Session):

    """
    The get_image function returns the image with the given id.
        
    
    :param image_id : int: Get the image id from the url
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass in the database session
    :return: A post object
    :doc-author: Trelent
    """
    return db.query(Post).filter(and_(Post.author_id == str(current_user.id), Post.id == image_id)).first()


async def del_image(image_id:int, db: Session, current_user: User ):
    """
    The del_image function deletes an image from the database.
        Args:
            image_id (int): The id of the post to be deleted.
            db (Session): A connection to a PostgreSQL database.
            current_user (User): The user who is making this request, as determined by FastAPI's authentication system.
    
    :param image_id:int: Specify the image to be deleted
    :param db: Session: Access the database
    :param current_user: User: Check if the user is authorized to delete the image
    :return: The dictionary {'msg': 'post deleted'}
    :doc-author: Trelent
    """
    try:
        image = db.query(Post).filter(Post.id == image_id).first()
        if image.author_id != current_user.id:        
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    db.delete(image)
    db.commit()
    return {'msg': 'Post deleted'}


async def put_image(image_id:int, new_description:str, current_user: User, db: Session):
    """
    The put_image function allows the user to update an image's description.
        The function takes in three parameters:
            - image_id: the id of the image that is being updated.
            - new_description: a string containing what will be used as the new description for this particular post. 
                This parameter is optional, and if it isn't provided, then no changes will be made to this field in our database. 
                If it is provided, then we'll use its value as our new description for this post.
    
    :param image_id:int: Identify the image that is to be updated
    :param new_description:str: Change the description of the image
    :param current_user: User: Check if the user is authorized to make changes to the image
    :param db: Session: Connect to the database
    :return: The new_images object
    :doc-author: Trelent
    """
    image = db.query(Post).filter(Post.id == image_id).first()
    if image.author_id != current_user.id:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    new_images = Post(id=image.id, description=new_description, author_id=current_user.id, image_url=image.image_url)
    db.delete(image)
    db.add(new_images)
    db.commit()
    db.refresh(new_images)
    return new_images