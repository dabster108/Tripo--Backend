from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    fullName: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?[1-9][0-9]{7,14}$")
    password: str = Field(min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", v):
            raise ValueError(
                "Password must contain at least:"
                "\n- 8 characters"
                "\n- One letter"
                "\n- One number"
                "\n- One special character (@$!%*#?&)"
            )
        return v

class UserResponse(BaseModel):
    message: str
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "User created successfully",
                "error": None
            }
        }