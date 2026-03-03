"""
Standalone discovery worker.

Run separately from the API server:
    cd backend
    python worker.py

The worker starts APScheduler and polls job sources every hour.
The FastAPI server also embeds the scheduler, so this standalone process
is only needed if you want to decouple the worker from the web server
(e.g. in production with separate processes).
"""
import logging
import signal
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

from app.worker.scheduler import start_scheduler, stop_scheduler  # noqa: E402


def _on_signal(sig, frame) -> None:
    logging.info("Received shutdown signal — stopping scheduler.")
    stop_scheduler()
    raise SystemExit(0)


def main() -> None:
    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    start_scheduler()
    logging.info("Worker running. Press Ctrl+C to stop.")

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
