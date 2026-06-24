from pydantic import BaseModel, EmailStr
from uuid import UUID


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_admin: bool
    is_active: bool

    model_config = {"from_attributes": True}