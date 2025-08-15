from __future__ import annotations

import asyncio
import json
import logging
from functools import wraps
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
import time
import uuid
import hashlib

from .config import load_config
from .logging_setup import setup_logging
from .tools.analytics import get_request_analytics, export_logs
from .tools.candidate import (
    candidate_assistant,
    resume_optimizer,
    interview_prep,
    salary_research,
)
from .tools.recruiter import (
    market_research,
    generate_job_post,
    generate_application_form,
    generate_quiz,
    generate_homework,
    generate_candidate_journey,
    generate_funnel_report,
)


def build_server() -> FastMCP:
    config = load_config()
    setup_logging(
        config.log_dir,
        config.log_level,
        webhook_url=config.log_webhook_url,
        webhook_secret=config.log_webhook_secret,
    )

    server = FastMCP("hiring-router")
    client_id = config.log_client_id

    def _register_with_logging(func):
        tool_name = func.__name__

        @wraps(func)
        def wrapped(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start = time.perf_counter()
            arg_keys = list(kwargs.keys())
            logger = logging.getLogger(__name__)

            logger.info(
                "tool_call",
                extra={
                    "extra": {
                        "event": "tool_call",
                        "request_id": request_id,
                        "client_id": client_id,
                        "tool": tool_name,
                        "arg_keys": arg_keys,
                    }
                },
            )
            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.info(
                    "tool_result",
                    extra={
                        "extra": {
                            "event": "tool_result",
                            "request_id": request_id,
                            "client_id": client_id,
                            "tool": tool_name,
                            "result_type": type(result).__name__,
                            "duration_ms": duration_ms,
                        }
                    },
                )
                return result
            except Exception:
                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.exception(
                    "tool_error",
                    extra={
                        "extra": {
                            "event": "tool_error",
                            "request_id": request_id,
                            "client_id": client_id,
                            "tool": tool_name,
                            "duration_ms": duration_ms,
                        }
                    },
                )
                raise

        server.tool()(wrapped)

    # Register tools with logging wrappers
    _register_with_logging(market_research)
    _register_with_logging(generate_job_post)
    _register_with_logging(generate_application_form)
    _register_with_logging(generate_quiz)
    _register_with_logging(generate_homework)
    _register_with_logging(generate_candidate_journey)
    _register_with_logging(generate_funnel_report)

    _register_with_logging(candidate_assistant)
    _register_with_logging(resume_optimizer)
    _register_with_logging(interview_prep)
    _register_with_logging(salary_research)

    _register_with_logging(get_request_analytics)
    _register_with_logging(export_logs)

    # Tool inventory
    @server.tool()
    def get_available_tools(user_type: Optional[str] = None) -> Dict[str, Any]:
        recruiter_tools = [
            "market_research",
            "generate_job_post",
            "generate_application_form",
            "generate_quiz",
            "generate_homework",
            "generate_candidate_journey",
            "generate_funnel_report",
        ]
        candidate_tools = [
            "candidate_assistant",
            "resume_optimizer",
            "interview_prep",
            "salary_research",
        ]
        analytics_tools = ["get_request_analytics", "export_logs"]
        full = {
            "recruiter": recruiter_tools,
            "candidate": candidate_tools,
            "analytics": analytics_tools,
        }
        if user_type and user_type.lower() in ("recruiter", "candidate"):
            return {user_type.lower(): full[user_type.lower()]}
        return full

    # Routing tool
    @server.tool()
    def route_hiring_task(user_type: str, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route a hiring task to appropriate tool based on decision tree.

        Args:
            user_type: "recruiter" or "candidate".
            task_description: Natural language description of the task.
            context: Optional structured context.
        """
        # Privacy-preserving logging for routing: no raw text recorded
        normalized = (task_description or "").lower()
        user_id = (context or {}).get("user_id") if isinstance(context, dict) else None
        user_hash = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest() if user_id is not None else None
        routed_to = None

        if user_type.lower() == "recruiter":
            if any(k in normalized for k in ["market research", "salary", "hh.ru", "research"]):
                routed_to = "market_research"
                result = market_research(**(context or {}))
            elif any(k in normalized for k in ["job post", "vacancy", "description"]):
                routed_to = "generate_job_post"
                result = generate_job_post(**(context or {}))
            elif any(k in normalized for k in ["application form", "apply form", "form"]):
                routed_to = "generate_application_form"
                result = generate_application_form(**(context or {}))
            elif any(k in normalized for k in ["quiz", "assessment", "test"]):
                routed_to = "generate_quiz"
                result = generate_quiz(**(context or {}))
            elif any(k in normalized for k in ["homework", "take-home", "assignment"]):
                routed_to = "generate_homework"
                result = generate_homework(**(context or {}))
            elif any(k in normalized for k in ["candidate journey", "process", "pipeline"]):
                routed_to = "generate_candidate_journey"
                result = generate_candidate_journey(**(context or {}))
            elif any(k in normalized for k in ["funnel", "report", "analytics"]):
                routed_to = "generate_funnel_report"
                result = generate_funnel_report(**(context or {}))
            else:
                logging.getLogger(__name__).info(
                    "route_hiring_task",
                    extra={
                        "extra": {
                            "event": "route_hiring_task",
                            "user_type": user_type,
                            "user_hash": user_hash,
                            "description_length": len(task_description or ""),
                            "context_keys": list((context or {}).keys()),
                            "routed_to": None,
                        }
                    },
                )
                return {"status": "unrouted", "message": "No matching route found; please refine the task description."}
        else:
            if any(k in normalized for k in ["resume", "cv", "ats"]):
                routed_to = "resume_optimizer"
                result = resume_optimizer(**(context or {}))
            elif any(k in normalized for k in ["interview", "prep", "questions"]):
                routed_to = "interview_prep"
                result = interview_prep(**(context or {}))
            elif any(k in normalized for k in ["salary", "market", "range"]):
                routed_to = "salary_research"
                result = salary_research(**(context or {}))
            else:
                routed_to = "candidate_assistant"
                result = candidate_assistant(task_description=task_description, **(context or {}))

        logging.getLogger(__name__).info(
            "route_hiring_task",
            extra={
                "extra": {
                    "event": "route_hiring_task",
                    "user_type": user_type,
                    "user_hash": user_hash,
                    "description_length": len(task_description or ""),
                    "context_keys": list((context or {}).keys()),
                    "routed_to": routed_to,
                }
            },
        )
        return result

    return server


def run() -> None:
    server = build_server()
    server.run()


if __name__ == "__main__":
    run()


