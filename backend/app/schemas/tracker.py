from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime, date


class JobApplicationCreate(BaseModel):
    job_title: str
    company: str
    status: str = "Inbox"
    type: str | None = None
    date_applied: date | None = None
    interview_date: date | None = None
    deadline: date | None = None
    keywords: List[str] = []
    link: str | None = None
    notes: str | None = None


class JobApplicationUpdate(BaseModel):
    job_title: str | None = None
    company: str | None = None
    status: str | None = None
    type: str | None = None
    date_applied: date | None = None
    interview_date: date | None = None
    deadline: date | None = None
    keywords: List[str] | None = None
    link: str | None = None
    notes: str | None = None


class JobApplicationResponse(JobApplicationCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}