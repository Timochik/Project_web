import cloudinary
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.utils.qr_code import get_qr_code_by_url
from src.database.models import Post, User
from src.conf.config import settings


async def transform_image(
    image_id: int,
    transform_params: dict,
    description: str,
    db: Session,
    current_user: User,
    service: cloudinary = cloudinary
) -> Post:
    """
    The transform_image function takes an image_id, transform_params, description and db as arguments.
    It then queries the database for a Post with the given id. If no such post exists it raises a 404 error.
    If the user is not authorized to access this post (i.e., if they are not its author) it raises a 403 error instead.
    The function then configures cloudinary using settings from settings module and builds an url for transformed image using 
    the public id of original image and transform params provided by user in request body (see docs/transformations). 
    Then it gets qr code url for new
    
    :param image_id: int: Specify the image that is to be transformed
    :param transform_params: dict: Pass in the transformation parameters
    :param description: str: Set the description of the new image
    :param db: Session: Access the database
    :param current_user: User: Get the user's id
    :param service: cloudinary: Pass in the cloudinary library
    :return: A new image with the transformation applied
    :doc-author: Trelent
    """
    image: Post = db.query(Post).filter(
        Post.id == image_id
    ).first()
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    if image.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    service.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    filename = image.image_url.split("/")[-1].split(".")[0]
    public_id = f'{settings.cloudinary_folder_name}/{filename}'

    url = service.CloudinaryImage(public_id=public_id).build_url(
        **transform_params
    )

    qr_code_url = await get_qr_code_by_url(url=url, service=service)

    new_image = Post(
        description=description,
        author_id=current_user.id,
        image_url=url,
        qr_code_url=qr_code_url,
        hashtags=image.hashtags
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image
