from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class ExperienceItem(BaseModel):
    title: str
    company: str
    years: float


class ProfileBase(BaseModel):
    raw_text: str
    skills: List[str] = []
    experience: List[ExperienceItem] = []


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    skills: List[str] | None = None
    experience: List[ExperienceItem] | None = None


class ProfileResponse(ProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}