from __future__ import annotations

import json
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import hmac
import hashlib
from typing import Optional

import requests


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            data.update(record.extra)
        return json.dumps(data, ensure_ascii=False)


class WebhookLogHandler(logging.Handler):
    def __init__(self, url: str, timeout_seconds: float = 2.0, secret: Optional[str] = None) -> None:
        super().__init__()
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.secret = secret

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        try:
            payload_str = self.format(record)
            # payload_str is JSON from JsonLogFormatter
            headers = {"Content-Type": "application/json; charset=utf-8"}
            if self.secret:
                signature = hmac.new(self.secret.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
                headers["X-Signature"] = f"sha256={signature}"

            self.session.post(
                self.url,
                data=payload_str.encode("utf-8"),
                headers=headers,
                timeout=self.timeout_seconds,
            )
        except Exception:
            # Never raise from a handler; swallow to avoid logging recursion
            pass


def setup_logging(log_dir: Path, level: str = "INFO", webhook_url: Optional[str] = None, webhook_secret: Optional[str] = None) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "requests.jsonl"

    handler = TimedRotatingFileHandler(
        filename=str(log_file), when="D", interval=1, backupCount=14, encoding="utf-8"
    )
    json_formatter = JsonLogFormatter()
    handler.setFormatter(json_formatter)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)

    if webhook_url:
        webhook_handler = WebhookLogHandler(webhook_url, secret=webhook_secret)
        webhook_handler.setFormatter(json_formatter)
        root.addHandler(webhook_handler)





