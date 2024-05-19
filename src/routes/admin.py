from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.db import get_db
from src.database.models import User, UserRole
from src.auth import get_current_active_admin
from src.schemas import UserOut

router = APIRouter()


class RoleChangeRequest(BaseModel):
    user_id: int
    new_role: UserRole


@router.put("/users/change-role/", response_model=UserOut)
async def change_user_role(
    request: RoleChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    user_to_update = db.query(User).filter(User.id == request.user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_to_update.role = request.new_role
    db.commit()
    db.refresh(user_to_update)
    return user_to_update