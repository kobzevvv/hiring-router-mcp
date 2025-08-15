from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    environment: str
    log_level: str
    log_dir: Path
    n8n_webhook_url: str | None
    hh_api_key: str | None


def load_config() -> AppConfig:
    load_dotenv()

    environment = os.getenv("ENVIRONMENT", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_dir = Path(os.getenv("LOG_DIR", "./hiring_logs")).expanduser().resolve()
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    hh_api_key = os.getenv("HH_API_KEY")

    log_dir.mkdir(parents=True, exist_ok=True)

    return AppConfig(
        environment=environment,
        log_level=log_level,
        log_dir=log_dir,
        n8n_webhook_url=n8n_webhook_url,
        hh_api_key=hh_api_key,
    )





