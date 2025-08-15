from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from ..config import load_config


def _read_logs() -> List[Dict[str, Any]]:
    config = load_config()
    log_file = config.log_dir / "requests.jsonl"
    if not log_file.exists():
        return []
    lines: List[Dict[str, Any]] = []
    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                lines.append(json.loads(line))
            except Exception:
                continue
    return lines


def get_request_analytics() -> Dict[str, Any]:
    logs = _read_logs()
    by_level = Counter([l.get("level") for l in logs])
    by_event = Counter([l.get("event") for l in logs if "event" in l])
    return {
        "total": len(logs),
        "by_level": dict(by_level),
        "by_event": dict(by_event),
    }


def export_logs() -> Dict[str, Any]:
    config = load_config()
    log_dir = str(config.log_dir)
    return {"export_path": log_dir}





