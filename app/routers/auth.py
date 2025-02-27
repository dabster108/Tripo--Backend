from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import schemas, models, database, security
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse
from ..core.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel
from typing import Optional

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Try to find user by username/email
    user = db.query(User).filter(
        (User.username == form_data.username) | 
        (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username}
    )

    # Return token and user data
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.get("/me")
async def get_current_user(
    current_user: models.User = Depends(security.get_current_user)
):
    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "fullName": current_user.full_name
        }
    }

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}

@router.post("/signup", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if username exists
        if db.query(User).filter(User.username == user.username).first():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Registration failed",
                    "error": "Username already taken"
                }
            )

        # Check if email exists
        if db.query(User).filter(User.email == user.email).first():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Registration failed",
                    "error": "Email already registered"
                }
            )
        
        # Check if phone exists
        if db.query(User).filter(User.phone == user.phone).first():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Registration failed",
                    "error": "Phone number already registered"
                }
            )

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            full_name=user.fullName,
            email=user.email,
            phone=user.phone,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        
        return {
            "message": "User created successfully",
            "error": None
        }
        
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Registration failed",
                "error": "An unexpected error occurred"
            }
        )