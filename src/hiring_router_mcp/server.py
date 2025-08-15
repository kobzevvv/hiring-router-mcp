from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

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
    setup_logging(config.log_dir, config.log_level)

    server = FastMCP("hiring-router")

    # Register tools
    # Register tools (logging of calls can be added later per tool)
    server.tool()(market_research)
    server.tool()(generate_job_post)
    server.tool()(generate_application_form)
    server.tool()(generate_quiz)
    server.tool()(generate_homework)
    server.tool()(generate_candidate_journey)
    server.tool()(generate_funnel_report)

    server.tool()(candidate_assistant)
    server.tool()(resume_optimizer)
    server.tool()(interview_prep)
    server.tool()(salary_research)

    server.tool()(get_request_analytics)
    server.tool()(export_logs)

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
        logging.getLogger(__name__).info(
            "route_hiring_task",
            extra={
                "extra": {
                    "event": "route_hiring_task",
                    "user_type": user_type,
                    "task_description": task_description,
                    "context": context or {},
                }
            },
        )

        normalized = (task_description or "").lower()
        if user_type.lower() == "recruiter":
            if any(k in normalized for k in ["market research", "salary", "hh.ru", "research"]):
                return market_research(**(context or {}))
            if any(k in normalized for k in ["job post", "vacancy", "description"]):
                return generate_job_post(**(context or {}))
            if any(k in normalized for k in ["application form", "apply form", "form"]):
                return generate_application_form(**(context or {}))
            if any(k in normalized for k in ["quiz", "assessment", "test"]):
                return generate_quiz(**(context or {}))
            if any(k in normalized for k in ["homework", "take-home", "assignment"]):
                return generate_homework(**(context or {}))
            if any(k in normalized for k in ["candidate journey", "process", "pipeline"]):
                return generate_candidate_journey(**(context or {}))
            if any(k in normalized for k in ["funnel", "report", "analytics"]):
                return generate_funnel_report(**(context or {}))
        else:
            if any(k in normalized for k in ["resume", "cv", "ats"]):
                return resume_optimizer(**(context or {}))
            if any(k in normalized for k in ["interview", "prep", "questions"]):
                return interview_prep(**(context or {}))
            if any(k in normalized for k in ["salary", "market", "range"]):
                return salary_research(**(context or {}))
            # Default for candidates
            return candidate_assistant(task_description=task_description, **(context or {}))

        return {"status": "unrouted", "message": "No matching route found; please refine the task description."}

    return server


def run() -> None:
    server = build_server()
    server.run()


if __name__ == "__main__":
    run()


