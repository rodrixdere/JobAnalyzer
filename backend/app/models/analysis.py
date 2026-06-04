import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    job_title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    job_text = Column(Text, nullable=False)
    required_skills = Column(JSONB, nullable=False, default=list)
    matching_skills = Column(JSONB, nullable=False, default=list)
    missing_skills = Column(JSONB, nullable=False, default=list)
    match_score = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)

    user = relationship("User", back_populates="analyses")