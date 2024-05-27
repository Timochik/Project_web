from typing import List
import uuid
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Post, User
from src.utils.qr_code import get_qr_code_by_url
from src.repository.tags import get_or_create_tag
from src.conf.config import settings
from src.services.auth import check_is_admin_or_moderator


cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

async def create_images_post(description: str, hashtags: List[str], user: User, db: Session, file: UploadFile)-> Post:
    """
    The create_images_post function creates a new post with the given description, hashtags, user and db.
        Args:
            description (str): The text of the post.
            hashtags (List[str]): A list of tags for this post.  Each tag is a string without spaces or special characters.  For example: [&quot;#funny&quot;, &quot;#cat&quot;]
            user (User): The author of this post as an instance of User class from models/user module in database_models folder in main directory.  
            This argument is passed by reference to the function so that it can be used to access information
    
    :param description: str: Pass in the description of the post
    :param hashtags: List[str]: Get the hashtags from the request body
    :param user: User: Get the user id of the author
    :param db: Session: Pass the database session to the function
    :param file: UploadFile: Upload the image to cloudinary
    :return: An object of the post class
    :doc-author: Trelent
    """
    dbtags = []
    for tag in hashtags:
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
    

async def get_images(user_id: int, db: Session):
    """
    The get_images function returns all images that the current user has uploaded.
            
        
        
    
    :param user_id: int: Get the current user's id
    :param db: Session: Access the database
    :return: All images that the current user has uploaded
    :doc-author: Trelent
    """
    return db.query(Post).filter(Post.author_id == str(user_id)).all()

async def get_image(image_id : int, user_id: User, db: Session):
    """
    The get_image function returns the image with the given id.
            
        
        
    
    :param image_id : int: Get the image id from the url
    :param user_id: User: Get the current user from the database
    :param db: Session: Pass in the database session
    :return: The image with the given id
    :doc-author: Trelent
    """
    return db.query(Post).filter(and_(Post.author_id == str(user_id), Post.id == image_id)).first()


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
    :return: A dictionary with the key 'msg' and value 'post deleted'
    :doc-author: Trelent
    """
    try:
        image = db.query(Post).filter(Post.id == image_id).first()
        if (not await check_is_admin_or_moderator(current_user) and
            image.author_id != current_user.id):
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
    
    :param image_id:int: Identify the image that is to be deleted
    :param new_description:str: Change the description of the image
    :param current_user: User: Check if the user is authorized to make changes to the image
    :param db: Session: Connect to the database
    :return: The new_images object
    :doc-author: Trelent
    """
    image = db.query(Post).filter(Post.id == image_id).first()
    if (not await check_is_admin_or_moderator(current_user) and
            image.author_id != current_user.id):      
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    image.description = new_description
    db.commit()
    db.refresh(image)
    return image
