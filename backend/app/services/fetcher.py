import time
from collections import deque
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from app.core.config import get_settings

_ALLOWED_HOST_HINTS = ("greenhouse.io", "lever.co", "workable.com")
_REQUEST_TIMES: deque[float] = deque(maxlen=200)


def _rate_limit() -> None:
    settings = get_settings()
    now = time.time()
    window = 60.0
    while _REQUEST_TIMES and now - _REQUEST_TIMES[0] > window:
        _REQUEST_TIMES.popleft()
    if len(_REQUEST_TIMES) >= settings.fetch_rate_limit_per_minute:
        sleep_for = max(0.0, window - (now - _REQUEST_TIMES[0]))
        time.sleep(min(sleep_for, 2.0))
    _REQUEST_TIMES.append(time.time())


def _robots_allowed(url: str) -> bool:
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
        return parser.can_fetch("JobCopilotBot", url)
    except Exception:
        return False


def source_is_compliant(url: str) -> bool:
    hostname = urlparse(url).netloc.lower()
    return any(h in hostname for h in _ALLOWED_HOST_HINTS)


def fetch_job_text(url: str) -> str:
    if not source_is_compliant(url):
        raise ValueError("URL host is not in allowed compliant sources. Paste JD text instead.")
    if not _robots_allowed(url):
        raise ValueError("robots.txt disallows fetching this URL.")

    _rate_limit()
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "JobCopilotBot/1.0"})
    response.raise_for_status()

    html = response.text
    stripped = " ".join(html.replace("<", " <").split())
    return stripped[:12000]
