from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.worker.discovery import run_discovery
from app.worker.scheduler import get_scheduler

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/run")
def trigger_discovery(_: str = Depends(get_current_user)) -> dict:
    """Manually trigger a discovery run without waiting for the hourly schedule."""
    return run_discovery()


@router.get("/status")
def discovery_status(_: str = Depends(get_current_user)) -> dict:
    """Return next scheduled run time and whether the scheduler is active."""
    scheduler = get_scheduler()
    if not scheduler.running:
        return {"scheduler_running": False, "next_run": None}

    job = scheduler.get_job("job_discovery")
    next_run = job.next_run_time.isoformat() if job and job.next_run_time else None
    return {"scheduler_running": True, "next_run": next_run}
