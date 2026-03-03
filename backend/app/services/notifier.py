import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

from app.core.config import get_settings

if TYPE_CHECKING:
    from app.models import Job

logger = logging.getLogger(__name__)


def _build_email(job: "Job", score: float) -> MIMEMultipart:
    settings = get_settings()
    sender = settings.smtp_from or settings.smtp_username or "noreply"
    recipient = settings.notify_email_to or ""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Job Match {score:.0f}% — {job.title} at {job.company}"
    msg["From"] = sender
    msg["To"] = recipient

    plain = (
        f"New job match found!\n\n"
        f"Title:   {job.title}\n"
        f"Company: {job.company}\n"
        f"Score:   {score:.1f}%\n"
        f"URL:     {job.url or 'N/A'}\n\n"
        f"Review & apply: http://localhost:3000/jobs/{job.id}\n"
    )
    html = f"""
    <html><body style="font-family:sans-serif;max-width:500px">
      <h2 style="color:#1a73e8">New Job Match: {score:.0f}%</h2>
      <table style="border-collapse:collapse;width:100%">
        <tr><td style="padding:6px;font-weight:bold">Title</td><td style="padding:6px">{job.title}</td></tr>
        <tr style="background:#f8f9fa"><td style="padding:6px;font-weight:bold">Company</td><td style="padding:6px">{job.company}</td></tr>
        <tr><td style="padding:6px;font-weight:bold">Match Score</td><td style="padding:6px;color:#1a73e8;font-weight:bold">{score:.1f}%</td></tr>
        <tr style="background:#f8f9fa"><td style="padding:6px;font-weight:bold">URL</td>
            <td style="padding:6px"><a href="{job.url or '#'}">{job.url or 'N/A'}</a></td></tr>
      </table>
      <p style="margin-top:20px">
        <a href="http://localhost:3000/jobs/{job.id}"
           style="background:#1a73e8;color:white;padding:10px 20px;text-decoration:none;border-radius:4px">
          Review &amp; Apply →
        </a>
      </p>
    </body></html>
    """
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


def send_match_notification(job: "Job", score: float) -> bool:
    """
    Send an email alert for a high-match job.
    Returns True if the email was sent, False otherwise.

    Requires in .env:
      SMTP_USERNAME, SMTP_PASSWORD, NOTIFY_EMAIL_TO
    For Gmail use an App Password (myaccount.google.com/apppasswords).
    """
    settings = get_settings()
    if not all([settings.smtp_username, settings.smtp_password, settings.notify_email_to]):
        logger.debug("[notifier] Email not configured — skipping notification.")
        return False

    try:
        msg = _build_email(job, score)
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(msg["From"], settings.notify_email_to, msg.as_string())
        logger.info(f"[notifier] Sent alert for '{job.title}' @ {job.company} ({score:.1f}%)")
        return True
    except Exception as exc:
        logger.warning(f"[notifier] Failed to send email: {exc}")
        return False
