"""
Discovery job: fetch → score → persist → notify.

Called by the scheduler every hour and can also be triggered manually
via POST /discovery/run.
"""
import logging

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models import Job, JobStatus, ResumeProfile
from app.schemas import JobExtracted, ResumeStructured
from app.services.job_extractor import extract_job_details
from app.services.job_sources import fetch_all_sources
from app.services.matcher import score_job
from app.services.notifier import send_match_notification

logger = logging.getLogger(__name__)


def _load_latest_resume(db: Session) -> ResumeStructured | None:
    profile = db.query(ResumeProfile).order_by(desc(ResumeProfile.created_at)).first()
    if not profile:
        return None
    return ResumeStructured(
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


def _url_exists(db: Session, url: str) -> bool:
    return db.query(Job.id).filter(Job.url == url).first() is not None


def run_discovery() -> dict:
    """
    Main discovery routine. Returns a summary dict:
      { "status": "ok"|"disabled"|"no_resume", "fetched": n, "new": n, "notified": n }
    """
    settings = get_settings()

    if not settings.discovery_enabled:
        logger.info("[discovery] Disabled — set DISCOVERY_ENABLED=true to activate.")
        return {"status": "disabled", "fetched": 0, "new": 0, "notified": 0}

    greenhouse = [c for c in settings.discovery_greenhouse_companies.split(",") if c.strip()]
    lever = [c for c in settings.discovery_lever_companies.split(",") if c.strip()]

    logger.info(
        f"[discovery] Starting run — query='{settings.discovery_search_terms}' "
        f"location='{settings.discovery_location}' "
        f"greenhouse={greenhouse} lever={lever}"
    )

    listings = fetch_all_sources(
        search_terms=settings.discovery_search_terms,
        location=settings.discovery_location,
        greenhouse_companies=greenhouse,
        lever_companies=lever,
    )
    logger.info(f"[discovery] Fetched {len(listings)} raw listings across all sources.")

    db = SessionLocal()
    try:
        resume = _load_latest_resume(db)
        if not resume:
            logger.warning("[discovery] No resume profile found — upload one via /resume/upload first.")
            return {"status": "no_resume", "fetched": len(listings), "new": 0, "notified": 0}

        new_count = 0
        notified_count = 0

        for listing in listings:
            if not listing.url or not listing.jd_text.strip():
                continue

            if _url_exists(db, listing.url):
                continue  # already imported

            extracted: JobExtracted = extract_job_details(listing.jd_text)
            job_score, explanation = score_job(resume, extracted, listing.jd_text)

            job = Job(
                source=listing.source,
                title=listing.title,
                company=listing.company,
                url=listing.url,
                jd_text=listing.jd_text,
                extracted=extracted.model_dump(),
                score=job_score,
                score_explanation=explanation,
                status=JobStatus.discovered,
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            new_count += 1

            logger.info(
                f"[discovery] + '{job.title}' @ {job.company} "
                f"(score={job_score:.1f}, source={listing.source})"
            )

            if job_score >= settings.notify_score_threshold:
                if send_match_notification(job, job_score):
                    notified_count += 1

        logger.info(
            f"[discovery] Run complete — fetched={len(listings)} new={new_count} notified={notified_count}"
        )
        return {"status": "ok", "fetched": len(listings), "new": new_count, "notified": notified_count}

    finally:
        db.close()
