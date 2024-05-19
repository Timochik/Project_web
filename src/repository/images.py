from typing import List

from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.models import Hashtag, Post, User

from sqlalchemy import and_
import cloudinary
import cloudinary.uploader

async def create_images_post(description, hashtags, user: User, db: Session, file: UploadFile)-> Post: # user: User,
    result = cloudinary.uploader.upload(file.file)     
    images = Post(description=description, author_id=user.id, image_url=result['secure_url']) #  hashtags=tags,
    db.add(images)
    db.commit()
    db.refresh(images)
    return images
