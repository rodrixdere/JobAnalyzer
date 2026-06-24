from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class AdminUserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_admin: bool
    last_seen: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminCreateUser(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False


class AdminToggleUser(BaseModel):
    is_active: bool