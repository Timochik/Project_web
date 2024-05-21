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
    return await repository_images.create_images_post(description, hashtags, current_user, db,  file)

@router.get("/get_image")
async def get_image(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await repository_images.get_images(current_user, db)

@router.delete("/delete_image")
async def delete_image(image_id: str , db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await repository_images.del_images(image_id, db, current_user)

@router.put("/edit_description_image")
async def delete_image(image_id: str , new_description: str, 
                       db: Session = Depends(get_db), 
                       current_user: User = Depends(auth_service.get_current_user)):
    return await repository_images.put_images(image_id, new_description, current_user, db)

@router.get("/images/crop")
async def crop_image_view(image_id: str, width: int, height: int):
    """
    Обрізає зображення за заданими шириною та висотою.


    Args:
        image_id: Ідентифікатор зображення.
        width: Ширина обрізаного зображення.
        height: Висота обрізаного зображення.


    Returns:
        JSON-відповідь з URL-адресою обрізаного зображення.
    """
    image_path = f"src/server/{image_id}.jpg"
    manipulated_url = await crop_image(image_path, width=width, height=height)
    return {"url": manipulated_url}


@router.get("/images/effect")
async def apply_effect_view( image_id: str, effect: str):
    """
    Застосовує ефект до зображення.


    Args:
        image_id: Ідентифікатор зображення.
        effect: Назва ефекту (наприклад, "sepia", "vignette").
        **kwargs: Додаткові аргументи для ефекту.


    Returns:
        JSON-відповідь з URL-адресою зображення з ефектом.
    """
    image_path = f"src/server/{image_id}.jpg"
    manipulated_url = await apply_effect(image_path, effect=effect)
    return {"url": manipulated_url}


@router.get("/images/roundcorners")
async def round_corners(image_id: str, radius: int):
    """
    Закругляє кути.


    Args:
        image_id: Ідентифікатор зображення.
        radius: Радіус зрізання кутів.


    Returns:
        JSON-відповідь з URL-адресою зображення без фону.
    """
    image_path = f"src/server/{image_id}.jpg"
    manipulated_url = await round_corners(image_path, "removebg")
    return {"url": manipulated_url}
