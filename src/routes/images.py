from pathlib import Path
import shutil
from fastapi import FastAPI, File, UploadFile, APIRouter
from fastapi.responses import FileResponse, HTMLResponse
from utils import crop_image, apply_effect, round_corners 

router = APIRouter(prefix='/images', tags=["images"])

@router.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    folder = Path('src/server')

    image_path = folder / file.filename

    with image_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": f"Image '{file.filename}' uploaded successfully!"}


@router.get("/images", response_class=HTMLResponse)
async def read_image(image_id: str):
    img_path = f"src/server/{image_id}.jpg"
    return FileResponse(img_path, media_type="image/jpeg")

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