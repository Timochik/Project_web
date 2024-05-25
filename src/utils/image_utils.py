import os
from cloudinary.uploader import upload
import cloudinary
from cloudinary import CloudinaryImage
from typing import List
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from src.utils.qr_code import get_qr_code_by_url
from src.repository.tags import get_or_create_tag

from src.database.models import Post, User
from dotenv import load_dotenv
load_dotenv()

from src.repository import images as repository_images

from src.conf.config import settings


async def crop_image(
    image_id: int,
    width: int,
    height: int,
    description: str,
    db: Session,
    current_user: User,
    service: cloudinary=cloudinary
)-> Post:

    """
    The crop_image function crops an image by the given width and height.
    
    :param image_id: int: Id of the image to be cropped
    :param width: int: Set the width of the image
    :param height: int: Set the height of the image
    :param description: str: Set the description of the new image
    :param db: Session: Access the database
    :param current_user: User: Get the user id of the current logged in user
    :param service: cloudinary: Mock the cloudinary library
    :return: The newly created image, which is then returned to the client
    :doc-author: Trelent
    """
    image:Post = db.query(Post).filter(
        Post.id == image_id
    ).first()
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    if image.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    service.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    filename = image.image_url.split("/")[-1].split(".")[0]
    public_id = f'{settings.cloudinary_folder_name}/{filename}'
    
    url = service.CloudinaryImage(public_id=public_id).build_url(
        height=height,
        width=width,
        crop="crop"
    )

    qr_code_url = await get_qr_code_by_url(url=url, service=service)

    new_image = Post(
        description=description,
        author_id=current_user.id,
        image_url=url,
        qr_code_url=qr_code_url,
        hashtags=image.hashtags
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


async def apply_effect(image_url, effect, description: str, hashtags: List[str], user: User, db: Session, file: UploadFile)-> Post:

  # Extract public ID from the image URL (assuming the format)
  public_id = image_url.split("/")[-1].split(".")[0]

  # Build the transformation string for the effect
  transformation = f"e_{effect}"

  # Construct the URL for the image with effect
  effect_url = f"{image_url.split('/upload')[0]}/upload/{transformation}/{public_id}"

  dbtags =[]
  for i in hashtags:
      tags_list = i.split(',')
  for tag in tags_list:
      dbtag = await get_or_create_tag(db, tag)
      dbtags.append(dbtag)
        
  url = effect_url
  qr_url = await get_qr_code_by_url(url)    
  images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=dbtags)
  db.add(images)
  db.commit()
  db.refresh(images)
  return images
  



async def round_corners(image_url, radius, description: str, hashtags: List[str], user: User, db: Session, file: UploadFile)-> Post:

  # Extract public ID from the image URL (assuming the format)
  public_id = image_url.split("/")[-1].split(".")[0]

  # Build the transformation string for rounded corners
  transformation = f"r_{radius}"

  # Construct the URL for the image with rounded corners
  rounded_url = f"{image_url.split('/upload')[0]}/upload/{transformation}/{public_id}"

  dbtags =[]
  for i in hashtags:
      tags_list = i.split(',')
  for tag in tags_list:
      dbtag = await get_or_create_tag(db, tag)
      dbtags.append(dbtag)
        
  url = rounded_url
  qr_url = await get_qr_code_by_url(url)    
  images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=dbtags)
  db.add(images)
  db.commit()
  db.refresh(images)
  return images
  
