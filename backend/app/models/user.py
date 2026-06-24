import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from datetime import datetime, timezone


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    analyses = relationship("Analysis", back_populates="user")
    job_applications = relationship("JobApplication", back_populates="user")