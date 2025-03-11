from pydantic import BaseModel, EmailStr, Field

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
class PasswordResetVerify(BaseModel):
    token: str
    
class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    
class PasswordResetResponse(BaseModel):
    message: str
    success: bool
    email: EmailStr