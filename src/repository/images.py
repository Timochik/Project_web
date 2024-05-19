from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.database.models import Post, User


import cloudinary
import cloudinary.uploader

async def create_images_post(description, hashtags, user: User, db: Session, file: UploadFile)-> Post: # user: User,
    result = cloudinary.uploader.upload(file.file)     
    images = Post(description=description, author_id=user.id, image_url=result['secure_url']) #  hashtags=tags,
    db.add(images)
    db.commit()
    db.refresh(images)
    return images

async def get_images(current_user: User, db: Session):
    return db.query(Post).filter(Post.author_id == str(current_user.id)).all()


async def put_images(image_id, new_description, current_user: User, db: Session):
    image = db.query(Post).filter(Post.id == image_id).first()
    if image.author_id != current_user.id:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    new_images = Post(id=image.id, description=new_description, author_id=current_user.id, image_url=image.image_url)
    db.delete(image)
    db.add(new_images)
    db.commit()
    db.refresh(new_images)
    return new_images