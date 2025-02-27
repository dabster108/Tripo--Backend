from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict