from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import ResumeProfile
from app.schemas import ResumeStructured, ResumeUploadResponse
from app.services.resume_parser import parse_resume

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await file.read()
    profile = parse_resume(file.filename or "resume.txt", content)

    db_obj = ResumeProfile(
        raw_text=profile.raw_text,
        contact=profile.contact,
        skills=profile.skills,
        years_experience=profile.years_experience,
        projects=profile.projects,
        employers=profile.employers,
        education=profile.education,
        keywords=profile.keywords,
        location_preferences=profile.location_preferences,
        work_auth=profile.work_auth,
        links=profile.links,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return ResumeUploadResponse(profile_id=db_obj.id, profile=ResumeStructured.model_validate(profile.model_dump()))
