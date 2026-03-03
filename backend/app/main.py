from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models import User
from app.worker.scheduler import start_scheduler, stop_scheduler
from app.routers import auth, discovery, jobs, resume

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.auth_username).first()
        if not existing:
            db.add(User(username=settings.auth_username, password_hash=get_password_hash(settings.auth_password)))
            db.commit()
    finally:
        db.close()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    stop_scheduler()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "warning": "Compliance required: no automated LinkedIn login, no credential storage, no CAPTCHA bypass."
    }


app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(discovery.router)
