# Job Application Copilot (Human-in-the-Loop)

Production-oriented starter for a compliant AI-assisted job application workflow.

## Compliance Guardrails (Hard Rules)
- No automated LinkedIn login.
- No credential collection/storage/replay for external job platforms.
- No CAPTCHA solving/bypass.
- No stealth automation.
- User must review each submission and click final submit manually.
- Fetching is rate-limited and restricted to compliant sources for URL ingestion.

## What This Includes
- Backend: FastAPI + SQLAlchemy (SQLite local, Postgres-ready)
- Frontend: Next.js (TypeScript)
- LLM layer: OpenAI-compatible wrapper with JSON-schema output contract
- Modules:
  - `resume_parser.py`
  - `job_extractor.py`
  - `matcher.py`
  - `generator.py`
  - `policy.yaml`
- DB models and starter Alembic migration
- Unit tests for extract/match/generate
- Local app auth (`/auth/login`)

## Repository Structure
- `backend/app/main.py` FastAPI app
- `backend/app/routers/` API routes
- `backend/app/services/` parsing/extraction/matching/generation/fetch/policy
- `backend/app/llm/` OpenAI-compatible client and prompt templates
- `backend/migrations/` migration scaffold + initial revision
- `backend/tests/` unit tests
- `backend/sample_data/` sample resume + job input
- `frontend/app/` Next.js app routes
- `policy.yaml` configurable autofill and ranking policy

## API Endpoints
- `POST /resume/upload`
- `POST /jobs/import`
- `GET /jobs`
- `GET /jobs/{id}`
- `POST /jobs/{id}/score`
- `POST /jobs/{id}/generate`
- `POST /jobs/{id}/status`

Extra:
- `POST /auth/login`
- `GET /health`

## Backend Setup
1. `cd backend`
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. `uvicorn app.main:app --reload --port 8000`

Optional migrations:
- `alembic -c migrations/alembic.ini upgrade head`

## Frontend Setup
1. `cd frontend`
2. `cp .env.local.example .env.local`
3. `npm install`
4. `npm run dev`
5. Open `http://localhost:3000`

## Basic Flow
1. Login to app (`admin` / `admin` by default; change in `.env`).
2. Upload resume on `/resume`.
3. Import jobs on `/jobs` (paste JD text or compliant source URLs).
4. Open a job detail page and click:
   - `Score Match`
   - `Generate`
5. Use guided checklist while applying manually in your browser.

## Policy File
Edit `/policy.yaml` for default answers:
- Work authorization
- Sponsorship
- Relocation
- Notice period
- Compensation range

## Sample Data
- `backend/sample_data/resume_sample.txt`
- `backend/sample_data/jobs_sample.csv`

## Tests
From `backend/`:
- `pytest`

## Inputs Needed From You
Before we tailor scoring/generation for your real search, provide:
1. Your resume file/text.
2. Target roles, locations, seniority, and dealbreakers.
3. Auto-fill policy preferences (work authorization, compensation range, relocation, notice period).
