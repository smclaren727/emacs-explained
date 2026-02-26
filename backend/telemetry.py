import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.config import AppConfig


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event: Dict[str, Any], config: AppConfig) -> None:
    if not config.enable_local_logs:
        return

    log_path = Path(config.local_log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {"timestamp": _utc_now_iso(), **event}
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")
