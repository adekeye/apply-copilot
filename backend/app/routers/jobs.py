from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Artifact, Job, JobStatus, ResumeProfile
from app.schemas import (
    GenerateRequest,
    GenerateResponse,
    JobExtracted,
    JobImportRequest,
    JobListResponse,
    JobResponse,
    ScoreResponse,
    StatusRequest,
    StatusResponse,
)
from app.services.fetcher import fetch_job_text
from app.services.generator import generate_answers, generate_checklist, generate_cover_letter
from app.services.job_extractor import extract_job_details
from app.services.matcher import score_job
from app.services.policy_service import load_policy

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _to_job_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        source=job.source,
        title=job.title,
        company=job.company,
        url=job.url,
        extracted=JobExtracted.model_validate(job.extracted),
        score=job.score,
        score_explanation=job.score_explanation,
        status=job.status,
        created_at=job.created_at,
    )


@router.post("/import", response_model=JobListResponse)
def import_jobs(payload: JobImportRequest, _: str = Depends(get_current_user), db: Session = Depends(get_db)):
    imported: list[JobResponse] = []
    for item in payload.jobs:
        jd_text = item.jd_text
        if not jd_text and item.url:
            jd_text = fetch_job_text(item.url)
        if not jd_text:
            raise HTTPException(status_code=400, detail="Each job item needs url or jd_text")

        extracted = extract_job_details(jd_text)
        job = Job(
            source=item.source,
            title=item.title or "Unknown",
            company=item.company or "Unknown",
            url=item.url,
            jd_text=jd_text,
            extracted=extracted.model_dump(),
            status=JobStatus.discovered,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        imported.append(_to_job_response(job))

    return JobListResponse(items=imported)


@router.get("", response_model=JobListResponse)
def list_jobs(
    status: JobStatus | None = Query(default=None),
    min_score: float | None = Query(default=None),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Job).order_by(desc(Job.updated_at))
    if status:
        query = query.filter(Job.status == status)
    if min_score is not None:
        query = query.filter(Job.score >= min_score)
    jobs = query.all()
    return JobListResponse(items=[_to_job_response(job) for job in jobs])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, _: str = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_job_response(job)


@router.post("/{job_id}/score", response_model=ScoreResponse)
def score(job_id: int, _: str = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = db.query(ResumeProfile).order_by(desc(ResumeProfile.created_at)).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Upload a resume first")

    from app.schemas import ResumeStructured

    resume = ResumeStructured(
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
    extracted = JobExtracted.model_validate(job.extracted)

    total, explanation = score_job(resume, extracted)
    job.score = total
    job.score_explanation = explanation
    db.add(job)
    db.commit()

    return ScoreResponse(score=total, explanation=explanation)


@router.post("/{job_id}/generate", response_model=GenerateResponse)
def generate(
    job_id: int,
    payload: GenerateRequest,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = db.query(ResumeProfile).order_by(desc(ResumeProfile.created_at)).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Upload a resume first")

    from app.schemas import ResumeStructured

    resume = ResumeStructured(
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
    extracted = JobExtracted.model_validate(job.extracted)
    policy = load_policy()

    cover_letter = generate_cover_letter(resume, job.title, job.company, extracted) if payload.include_cover_letter else None
    answers = generate_answers(policy, resume, extracted) if payload.include_answers else None
    checklist = generate_checklist()

    for kind, content in [("cover_letter", cover_letter), ("answers", answers)]:
        if not content:
            continue
        previous = (
            db.query(Artifact)
            .filter(Artifact.job_id == job.id, Artifact.kind == kind)
            .order_by(desc(Artifact.version))
            .first()
        )
        version = (previous.version + 1) if previous else 1
        db.add(Artifact(job_id=job.id, kind=kind, version=version, content=content))

    job.status = JobStatus.drafted
    db.add(job)
    db.commit()

    return GenerateResponse(cover_letter=cover_letter, answers=answers, checklist=checklist)


@router.post("/{job_id}/status", response_model=StatusResponse)
def update_status(job_id: int, payload: StatusRequest, _: str = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = payload.status
    db.add(job)
    db.commit()
    return StatusResponse(id=job.id, status=job.status)
