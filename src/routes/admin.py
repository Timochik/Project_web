from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.db import get_db
from src.database.models import User, UserRole
from src.services.auth import auth_service, is_admin
from src.schemas import UserOut, RoleChangeRequest


router = APIRouter(prefix="/admin", tags=["admin"])


@router.put("/change-role", response_model=UserOut)
async def change_user_role(
    request: RoleChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    # if current_user.role != UserRole.admin:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

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
    current_user: User = Depends(auth_service.get_current_user)
):
    if current_user.role != UserRole.admin:
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
        current_user: User = Depends(auth_service.get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    user_to_unban = db.query(User).filter(User.id == user_id).first()
    if not user_to_unban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_to_unban.is_active = True
    db.commit()
    db.refresh(user_to_unban)
    return user_to_unban