from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import (
    PostCommentReques,
    GetCommentResponce,
    PutCommentReques
)
from src.database.models import User, Post, Comments, UserRole
from src.services.auth import auth_service


router = APIRouter(prefix='/comments', tags=["comments"])


@router.post(
    "/",
    response_model=GetCommentResponce,
    status_code=status.HTTP_201_CREATED,
)
async def post_comment(
    body: PostCommentReques,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The post_comment function creates a new comment for the image with the given id.
    The user who created this comment is determined by the JWT token in the request header.
    
    :param body: PostCommentReques: Get the data from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: A comment
    :doc-author: Trelent
    """
    image = db.query(Post).filter(
        Post.id == body.image_id
    ).first()
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    comment = Comments(
        text=body.text,
        image_id=image.id,
        user_id=current_user.id
    )
    db.add(comment)
    db.commit()
    return comment


@router.get(
    "/{comment_id}",
    response_model=GetCommentResponce
)
async def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """
    The get_comment function returns a comment with the given id.
    If no such comment exists, it raises an HTTP 404 error.
    
    :param comment_id: int: Specify the comment id
    :param db: Session: Get the database session
    :return: A comment with the given id
    :doc-author: Trelent
    """
    comment = db.query(Comments).filter(
        Comments.id == comment_id
    ).first()
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@router.get(
    "/by-image/{image_id}",
    response_model=List[GetCommentResponce]
)
async def get_comments_by_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    The get_comments_by_image function returns a list of comments for the image with the given id.
    If no image is found, it raises an HTTPException with status code 404 and detail 'Image not found';.
    
    :param image_id: int: Get the image id from the url
    :param db: Session: Get the database session
    :return: A list of comments for the image with the given id
    :doc-author: Trelent
    """
    image = db.query(Post).filter(
        Post.id == image_id
    ).first()
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    comments = db.query(Comments).filter(
        Comments.image_id == image.id
    ).all()
    return comments


@router.get(
    "/by-user/{user_id}",
    response_model=List[GetCommentResponce]
)
async def get_comments_by_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    The get_comments_by_user function returns a list of comments made by the user with the given ID.
    If no such user exists, it raises an HTTP 404 error.
    
    :param user_id: int: Specify the user_id of the user we want to get comments for
    :param db: Session: Get the database session
    :return: A list of comments made by the user with the given id
    :doc-author: Trelent
    """
    user = db.query(User).filter(
        User.id == user_id
    ).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    comments = db.query(Comments).filter(
        Comments.user_id == user.id
    ).all()
    return comments


@router.put(
    "/",
    response_model=GetCommentResponce,
)
async def change_comment(
    body: PutCommentReques,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The change_comment function allows a user to change the text of their comment.
        
        
    
    :param body: PutCommentReques: Get the new text for the comment
    :param db: Session: Get a database session
    :param current_user: User: Get the user who is currently logged in
    :return: The comment that was updated
    :doc-author: Trelent
    """
    comment = db.query(Comments).filter(
        Comments.id == body.comment_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    comment.text = body.new_text
    comment.updated_at = datetime.now()
    db.commit()
    return comment


@router.delete(
    "/{comment_id}",
    response_model=GetCommentResponce
)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The delete_comment function deletes a comment from the database.
        
        
    
    :param comment_id: int: Specify the id of the comment to be edited
    :param db: Session: Get a database session
    :param current_user: User: Get the current user from the database
    :return: The deleted comment
    :doc-author: Trelent
    """
    if current_user.role not in (UserRole.admin, UserRole.moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    comment = db.query(Comments).filter(
        Comments.id == comment_id
    ).first()
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    db.delete(comment)
    db.commit()
    return comment
