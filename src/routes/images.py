from pathlib import Path
import shutil
from fastapi import FastAPI, File, UploadFile, APIRouter
from fastapi.responses import FileResponse, HTMLResponse

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