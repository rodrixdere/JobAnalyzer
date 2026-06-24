import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class JobApplication(Base, TimestampMixin):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Inbox")
    type = Column(String, nullable=True)
    date_applied = Column(Date, nullable=True)
    interview_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    keywords = Column(JSONB, nullable=False, default=list)
    link = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="job_applications")