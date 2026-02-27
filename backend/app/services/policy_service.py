from pathlib import Path
from typing import Any

import yaml

from app.core.config import get_settings


def load_policy() -> dict[str, Any]:
    settings = get_settings()
    policy_file = Path(settings.policy_path)
    if not policy_file.exists():
        return {}
    with policy_file.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
