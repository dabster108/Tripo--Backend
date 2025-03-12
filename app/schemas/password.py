from pydantic import BaseModel, EmailStr
from typing import Optional

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class StepCompletionResponse(BaseModel):
    message: str
    success: bool
    next_step: str
    user_id: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str