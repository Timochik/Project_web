import os
from cloudinary.uploader import upload
from cloudinary import CloudinaryImage
from typing import List
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from src.repository.qr_code import get_qr_code_by_url
from src.repository.tags import get_or_create_tag
from src.repository.images import get_image
from src.database.models import Post, User

from src.repository import images as repository_images

async def crop_image(image_id, width, height, description: str, user: User, db: Session)-> Post:

  image = get_image(image_id, user, db)

  cropped_url = CloudinaryImage(image).image(transformation=[{"width": width, "height": height, "crop": "fill"}])
  print(f"Secure URL: {cropped_url}")

  tags = [hashtag.name for hashtag in image.hashtags]
        
  url = cropped_url
  qr_url = await get_qr_code_by_url(url)    
  images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=tags)
  db.add(images)
  db.commit()
  db.refresh(images)
  return images



async def apply_effect(image_id, effect, description: str, user: User, db: Session)-> Post:
  
  image = get_image(image_id, user, db)

  # Extract public ID from the image URL (assuming the format)
  effected_url = CloudinaryImage(image).image(transformation=[{"effect": effect}])
  print(f"Secure URL: {effected_url}")

  tags = [hashtag.name for hashtag in image.hashtags]
        
  url = effected_url
  qr_url = await get_qr_code_by_url(url)    
  images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=tags)
  db.add(images)
  db.commit()
  db.refresh(images)
  return images
  



async def round_corners(image_id, radius, description: str, user: User, db: Session)-> Post:
  
  image = get_image(image_id, user, db)

  rounded_url = CloudinaryImage(image).image(transformation=[{"radius": radius}])
  print(f"Secure URL: {rounded_url}")

  tags = [hashtag.name for hashtag in image.hashtags]
        
  url = rounded_url
  qr_url = await get_qr_code_by_url(url)    
  images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=tags)
  db.add(images)
  db.commit()
  db.refresh(images)
  return images


  
