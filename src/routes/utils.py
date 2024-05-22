import os
from cloudinary.uploader import upload
import cloudinary
from typing import List
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from src.repository.qr_code import get_qr_code_by_url
from src.repository.tags import get_or_create_tag

from src.database.models import Post, User
from dotenv import load_dotenv
load_dotenv()

from src.repository import images as repository_images

async def crop_image(image_url, width, height, description: str, hashtags: List[str], user: User, db: Session, file: UploadFile)-> Post:

  # Extract public ID from the image URL (assuming the format)
  public_id = image_url.split("/")[-1].split(".")[0]

  # Generate the transformation string for cropping
  transformation = f"c_crop,w_{width},h_{height}"

  # Construct the URL for the cropped image
  cropped_url = f"{image_url.split('/upload')[0]}/upload/{transformation}/{public_id}"
  print(f"Secure URL: {cropped_url}")

  dbtags =[]
  for i in hashtags:
      tags_list = i.split(',')
  for tag in tags_list:
      dbtag = await get_or_create_tag(db, tag)
      dbtags.append(dbtag)
        
  url = cropped_url
  qr_url = await get_qr_code_by_url(url)    
  images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=dbtags)
  db.add(images)
  db.commit()
  db.refresh(images)
  return images



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
  
