"""
Public job feed fetchers.

Sources used:
  - Indeed RSS  — public syndication feed, no auth required.
  - Greenhouse  — public job board JSON API (boards-api.greenhouse.io).
  - Lever       — public postings API (api.lever.co/v0/postings).

All requests use a shared rate limiter inherited from fetcher.py.
"""
import logging
import re
import time
from dataclasses import dataclass
from urllib.parse import urlencode

import feedparser
import httpx

logger = logging.getLogger(__name__)

_USER_AGENT = "JobCopilotBot/1.0"
_TIMEOUT = 15.0
# Shared simple rate limiter: minimum 1 second between requests
_last_request_time: float = 0.0


def _throttle() -> None:
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _last_request_time = time.time()


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def _get(url: str) -> httpx.Response:
    _throttle()
    with httpx.Client(timeout=_TIMEOUT, follow_redirects=True) as client:
        return client.get(url, headers={"User-Agent": _USER_AGENT})


@dataclass
class DiscoveredJob:
    title: str
    company: str
    url: str
    jd_text: str
    source: str


# ---------------------------------------------------------------------------
# Indeed RSS
# ---------------------------------------------------------------------------

def _parse_indeed_title(raw: str) -> tuple[str, str]:
    """Split 'Software Engineer - Google' → ('Software Engineer', 'Google')."""
    for sep in (" - ", " at ", " | "):
        if sep in raw:
            parts = raw.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return raw.strip(), "Unknown"


def fetch_indeed_rss(query: str, location: str, max_age_days: int = 1) -> list[DiscoveredJob]:
    """
    Fetch jobs from Indeed's public RSS feed.
    `max_age_days=1` returns only listings posted in the last 24 hours so
    hourly runs don't re-import stale results.
    """
    params = {"q": query, "l": location, "fromage": str(max_age_days), "limit": "25"}
    url = f"https://www.indeed.com/rss?{urlencode(params)}"
    try:
        resp = _get(url)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    except Exception as exc:
        logger.warning(f"[job_sources] Indeed RSS error: {exc}")
        return []

    jobs: list[DiscoveredJob] = []
    for entry in feed.entries:
        title, company = _parse_indeed_title(entry.get("title", "Unknown"))
        link = entry.get("link", "")
        summary = _strip_html(entry.get("summary", ""))
        if not link:
            continue
        jobs.append(DiscoveredJob(title=title, company=company, url=link, jd_text=summary, source="indeed"))

    logger.info(f"[job_sources] Indeed: {len(jobs)} listings for '{query}' in '{location}'")
    return jobs


# ---------------------------------------------------------------------------
# Greenhouse public board API
# ---------------------------------------------------------------------------

def fetch_greenhouse_jobs(company_slug: str) -> list[DiscoveredJob]:
    """
    Fetch all open jobs from a company's public Greenhouse board.
    API: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"
    try:
        resp = _get(url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning(f"[job_sources] Greenhouse '{company_slug}' error: {exc}")
        return []

    jobs: list[DiscoveredJob] = []
    for item in data.get("jobs", []):
        content = _strip_html(item.get("content", ""))[:8000]
        job_url = item.get("absolute_url", "")
        if not job_url:
            continue
        jobs.append(
            DiscoveredJob(
                title=item.get("title", "Unknown"),
                company=company_slug.replace("-", " ").title(),
                url=job_url,
                jd_text=content,
                source=f"greenhouse:{company_slug}",
            )
        )

    logger.info(f"[job_sources] Greenhouse '{company_slug}': {len(jobs)} listings")
    return jobs


# ---------------------------------------------------------------------------
# Lever public postings API
# ---------------------------------------------------------------------------

def fetch_lever_jobs(company_slug: str) -> list[DiscoveredJob]:
    """
    Fetch all open jobs from a company's public Lever board.
    API: https://api.lever.co/v0/postings/{slug}?mode=json
    """
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    try:
        resp = _get(url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning(f"[job_sources] Lever '{company_slug}' error: {exc}")
        return []

    jobs: list[DiscoveredJob] = []
    for item in data:
        text_parts = [
            item.get("text", ""),
            item.get("descriptionPlain", ""),
            " ".join(lst.get("content", "") for lst in item.get("lists", [])),
        ]
        jd_text = " ".join(filter(None, text_parts))[:8000]
        job_url = item.get("hostedUrl", "")
        if not job_url:
            continue
        jobs.append(
            DiscoveredJob(
                title=item.get("text", "Unknown"),
                company=company_slug.replace("-", " ").title(),
                url=job_url,
                jd_text=jd_text,
                source=f"lever:{company_slug}",
            )
        )

    logger.info(f"[job_sources] Lever '{company_slug}': {len(jobs)} listings")
    return jobs


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def fetch_all_sources(
    search_terms: str,
    location: str,
    greenhouse_companies: list[str],
    lever_companies: list[str],
) -> list[DiscoveredJob]:
    results: list[DiscoveredJob] = []
    results.extend(fetch_indeed_rss(search_terms, location))
    for slug in greenhouse_companies:
        results.extend(fetch_greenhouse_jobs(slug.strip()))
    for slug in lever_companies:
        results.extend(fetch_lever_jobs(slug.strip()))
    return results
