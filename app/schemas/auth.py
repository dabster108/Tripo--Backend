from pydantic import BaseModel, EmailStr, Field, validator
import re
from typing import Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class LoginResponse(BaseModel):
    message: str
    token: TokenData
    user: Dict[str, Any]

class InitialSignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
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

class InitialSignupResponse(BaseModel):
    message: str
    user_id: str
    email: str
    username: str
    verification_sent: bool

class VerificationRequest(BaseModel):
    code: str
    user_id: str

class VerificationResponse(BaseModel):
    message: str
    success: bool
    user_id: Optional[str] = None