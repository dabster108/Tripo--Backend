from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, validator
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Base, User
from . import database
from typing import Optional
import re

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # You can adjust this value (10-14 is common)
)

# Create database tables
Base.metadata.create_all(bind=database.engine)

# Input validation model
class UserCreate(BaseModel):
    username: str = Field(
        min_length=3, 
        max_length=20, 
        pattern="^[a-zA-Z0-9_-]+$"
    )
    fullName: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(
        pattern=r"^\+?[1-9][0-9]{7,14}$"
    )
    password: str = Field(min_length=8)

    @validator('password')
    def validate_password(cls, v):
        # Updated regex to require only one special character
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", v):
            raise ValueError(
                "Password must contain at least:"
                "\n- 8 characters"
                "\n- One letter"
                "\n- One number"
                "\n- One special character (@$!%*#?&)"
            )
        return v

# Response model
class UserResponse(BaseModel):
    message: str
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "User created successfully",
                "error": None
            }
        }

@app.post("/api/auth/signup", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(database.get_db)):
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
        hashed_password = pwd_context.hash(user.password)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)