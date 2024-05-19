from typing import List
from fastapi import APIRouter, Depends, File, HTTPException,UploadFile,status
import cloudinary.uploader
from src.database.models import Post, User
from src.database.db import get_db

from src.conf.config import settings
from src.repository import images as repository_images

import cloudinary
from sqlalchemy.orm import Session
from src.services.auth import auth_service
router = APIRouter(prefix='/images', tags=["images"])

cloudinary.config(
    cloud_name = settings.cloudinary_name,
    api_key = settings.cloudinary_api_key,
    api_secret = settings.cloudinary_api_secret
)

@router.post("/upload")
async def upload_file(description: str, hashtags: List[str], db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),   file: UploadFile = File(...)):
    return await repository_images.create_images_post(description, hashtags, current_user, db,  file)


@router.get("/get_image")
async def get_image(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await repository_images.get_images(current_user, db)


@router.delete("/delete_image")
async def delete_image(image_id: str ,db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    image = db.query(Post).filter(Post.id == image_id).first()
    if image.author_id != current_user.id:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    db.delete(image)
    db.commit()
    return {'msg': 'Post deleted'}


@router.put("/edit_description_image")
async def delete_image(image_id: str , new_description: str, 
                       db: Session = Depends(get_db), 
                       current_user: User = Depends(auth_service.get_current_user)):
    return await repository_images.put_images(image_id, new_description, current_user, db)
    
    
