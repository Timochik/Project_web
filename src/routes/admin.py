from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import is_admin
from src.schemas import UserOut, RoleChangeRequest


router = APIRouter(prefix="/admin", tags=["admin"])


@router.put("/change-role", response_model=UserOut)
async def change_user_role(
    request: RoleChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """
    The change_user_role function changes the role of a user.
    
    :param request: RoleChangeRequest: Pass the user_id and new_role parameters
    :param db: Session: Access the database
    :param current_user: User: Get the current user
    :return: The user object, which is the same as the one in get_user
    :doc-author: Trelent
    """
    if request.user_id == 1 or request.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    user_to_update = db.query(User).filter(User.id == request.user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_to_update.role = request.new_role
    db.commit()
    db.refresh(user_to_update)
    return user_to_update


@router.put("/ban/{user_id}", response_model=UserOut)
async def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """
    The ban_user function is used to ban a user.
    
    :param user_id: int: Specify the user id of the user to be banned
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: The banned user
    :doc-author: Trelent
    """
    if user_id == 1 or user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    user_to_ban = db.query(User).filter(User.id == user_id).first()
    if not user_to_ban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_to_ban.is_active = False
    db.commit()
    db.refresh(user_to_ban)
    return user_to_ban


@router.put("/unban/{user_id}", response_model=UserOut)
async def unban_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(is_admin)
):
    """
    The unban_user function takes a user_id and an optional db Session object.
    It returns the User object of the unbanned user.
    
    
    :param user_id: int: Specify the user id of the user to be banned
    :param db: Session: Access the database
    :param current_user: User: Ensure that the user is an admin
    :return: A user object
    :doc-author: Trelent
    """
    user_to_unban = db.query(User).filter(User.id == user_id).first()
    if not user_to_unban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_to_unban.is_active = True
    db.commit()
    db.refresh(user_to_unban)
    return user_to_unban
