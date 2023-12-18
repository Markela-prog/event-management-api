
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from datab.db import SessionLocal
from datab.security import get_current_user
from user.models import Users
from user.schemas import UserProfile, UpdateUserProfile, User

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/profile", response_model=UserProfile)
def read_profile(current_user: user_dependency, db: db_dependency):
    user = db.query(Users).filter(Users.id == current_user["id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/profile", response_model=UserProfile)
def update_profile(profile: UpdateUserProfile, current_user: user_dependency, db: db_dependency):
    user = db.query(Users).filter(Users.id == current_user["id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if profile.username is not None:
        # Check if the new username is already taken
        if db.query(Users).filter(Users.username == profile.username).first() is not None:
            raise HTTPException(status_code=400, detail="Username is already taken")
        user.username = profile.username
    if profile.email is not None:
        user.email = profile.email
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=List[User])
def get_all_users(db: db_dependency, skip: int = 0, limit: int = 100):
    users = db.query(Users).offset(skip).limit(limit).all()
    return users

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return {"User": user}

@router.get("/{user_id}")
def get_user_by_id(user_id: int, db: db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}
