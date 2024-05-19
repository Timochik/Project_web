from typing import List
from fastapi import APIRouter, Depends, File, Response, UploadFile, requests
import cloudinary.uploader
from fastapi.responses import HTMLResponse
from src.database.models import User
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

@router.post("/upload") # response_model=ImagesResponse
async def upload_file(description: str, hashtags: List[str], db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),   file: UploadFile = File(...)):
    return await repository_images.create_images_post(description, hashtags, current_user, db,  file)


