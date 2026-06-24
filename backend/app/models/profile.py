import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    raw_text = Column(Text, nullable=False)
    full_name = Column(String, nullable=True)
    professional_title = Column(String, nullable=True)
    email = Column(String, nullable=True)
    skills = Column(JSONB, nullable=False, default=list)
    experience = Column(JSONB, nullable=False, default=list)
    projects = Column(JSONB, nullable=False, default=list)
    education = Column(JSONB, nullable=False, default=list)
    languages = Column(JSONB, nullable=False, default=list)
    links = Column(JSONB, nullable=False, default=dict)

    user = relationship("User", back_populates="profile")