from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class ExperienceItem(BaseModel):
    title: str
    company: str
    years: float


class ProjectItem(BaseModel):
    name: str
    description: str
    technologies: List[str] = []


class EducationItem(BaseModel):
    degree: str
    institution: str
    year: int | None = None


class ProfileLinks(BaseModel):
    github: str | None = None
    linkedin: str | None = None
    portfolio: str | None = None


class ProfileBase(BaseModel):
    raw_text: str
    full_name: str | None = None
    professional_title: str | None = None
    email: str | None = None
    skills: List[str] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    education: List[EducationItem] = []
    languages: List[str] = []
    links: ProfileLinks = ProfileLinks()


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    professional_title: str | None = None
    email: str | None = None
    skills: List[str] | None = None
    experience: List[ExperienceItem] | None = None
    projects: List[ProjectItem] | None = None
    education: List[EducationItem] | None = None
    languages: List[str] | None = None
    links: ProfileLinks | None = None


class ProfileResponse(ProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}