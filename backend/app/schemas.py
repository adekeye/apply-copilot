from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models import JobStatus


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)


class ResumeStructured(BaseModel):
    contact: dict[str, Any]
    skills: list[str]
    years_experience: int = 0
    projects: list[str] = Field(default_factory=list)
    employers: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    location_preferences: list[str] = Field(default_factory=list)
    work_auth: str = "Unknown"
    links: list[str] = Field(default_factory=list)
    raw_text: str


class ResumeUploadResponse(BaseModel):
    profile_id: int
    profile: ResumeStructured


class JobImportItem(BaseModel):
    url: str | None = None
    jd_text: str | None = None
    source: str = "user"
    title: str | None = None
    company: str | None = None


class JobImportRequest(BaseModel):
    jobs: list[JobImportItem]


class JobExtracted(BaseModel):
    responsibilities: list[str] = Field(default_factory=list)
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    location: str = "Unknown"
    seniority: str = "Unknown"
    compensation: str | None = None


class JobResponse(BaseModel):
    id: int
    source: str
    title: str
    company: str
    url: str | None
    extracted: JobExtracted
    score: float | None
    score_explanation: dict[str, Any] | None
    status: JobStatus
    created_at: datetime


class JobListResponse(BaseModel):
    items: list[JobResponse]


class ScoreResponse(BaseModel):
    score: float
    explanation: dict[str, Any]


class GenerateRequest(BaseModel):
    include_cover_letter: bool = True
    include_answers: bool = True


class GenerateResponse(BaseModel):
    cover_letter: dict[str, Any] | None
    answers: dict[str, Any] | None
    checklist: list[str]


class StatusRequest(BaseModel):
    status: JobStatus


class StatusResponse(BaseModel):
    id: int
    status: JobStatus
