from pydantic import BaseModel, field_validator
from typing import List
from uuid import UUID
from datetime import datetime


class AnalysisCreate(BaseModel):
    job_text: str

    @field_validator('job_text')
    @classmethod
    def job_text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('job_text no puede estar vacío')
        return v


class AnalysisCreate(BaseModel):
    job_text: str


class AnalysisResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_title: str | None
    company: str | None
    job_text: str
    required_skills: List[str]
    matching_skills: List[str]
    missing_skills: List[str]
    match_score: int
    summary: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: UUID
    job_title: str | None
    company: str | None
    match_score: int
    summary: str
    created_at: datetime

    model_config = {"from_attributes": True}