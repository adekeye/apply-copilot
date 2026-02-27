from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class JobStatus(str, Enum):
    discovered = "discovered"
    saved = "saved"
    drafted = "drafted"
    applied = "applied"
    interview = "interview"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    contact: Mapped[dict] = mapped_column(JSON)
    skills: Mapped[list] = mapped_column(JSON)
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    projects: Mapped[list] = mapped_column(JSON)
    employers: Mapped[list] = mapped_column(JSON)
    education: Mapped[list] = mapped_column(JSON)
    keywords: Mapped[list] = mapped_column(JSON)
    location_preferences: Mapped[list] = mapped_column(JSON)
    work_auth: Mapped[str] = mapped_column(String(255), default="Unknown")
    links: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(100), default="user")
    title: Mapped[str] = mapped_column(String(255), default="Unknown")
    company: Mapped[str] = mapped_column(String(255), default="Unknown")
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    jd_text: Mapped[str] = mapped_column(Text)
    extracted: Mapped[dict] = mapped_column(JSON)
    score: Mapped[float | None] = mapped_column(nullable=True)
    score_explanation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus), default=JobStatus.discovered)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    artifacts: Mapped[list["Artifact"]] = relationship(back_populates="job")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    kind: Mapped[str] = mapped_column(String(100))
    version: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped[Job] = relationship(back_populates="artifacts")
