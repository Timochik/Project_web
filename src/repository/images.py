from typing import List
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.database.models import Post, User
from src.repository.qr_code import get_qr_code_by_url
from src.repository.tags import get_or_create_tag


import cloudinary
import cloudinary.uploader

async def create_images_post(description, hashtags: List[str], user: User, db: Session, file: UploadFile)-> Post: 
    dbtags =[]
    for i in hashtags:
        tags_list = i.split(',')
    for tag in tags_list:
        dbtag = await get_or_create_tag(db, tag)
        dbtags.append(dbtag)
        
    result = cloudinary.uploader.upload(file.file)
    url = result['secure_url']
    qr_url = await get_qr_code_by_url(url)    
    images = Post(description=description, author_id=user.id, image_url=url, qr_code_url=qr_url, hashtags=dbtags) #  hashtags=tags,
    db.add(images)
    db.commit()
    db.refresh(images)
    return images
    

async def get_images(current_user: User, db: Session):
    return db.query(Post).filter(Post.author_id == str(current_user.id)).all()

async def del_images(image_id, db: Session, current_user: User ):
    try:
        image = db.query(Post).filter(Post.id == image_id).first()
        if image.author_id != current_user.id:        
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")
    db.delete(image)
    db.commit()
    return {'msg': 'Post deleted'}

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