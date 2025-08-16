from __future__ import annotations

from typing import Any, Dict, List, Optional


def market_research(query: Optional[str] = None, location: Optional[str] = None, role: Optional[str] = None, experience_years: Optional[int] = None) -> Dict[str, Any]:
    """Guide for HH.ru market research and salary stats.

    Returns an instruction set that Claude can follow to help the user perform manual research now.
    """
    instructions = [
        "Open hh.ru and switch to the appropriate region.",
        f"Search for role: {role or query or 'e.g., Python разработчик'} in {location or 'target location'}.",
        "Filter by experience level and employment type as needed.",
        "Collect: number of vacancies, common skills, tech stack, seniority split.",
        "Check salary statistics page (Зарплаты) and record median, p25, p75.",
        "Summarize insights with bullet points and suggested compensation bands.",
    ]
    return {"type": "instructions", "steps": instructions}


def generate_job_post(company: Optional[str] = None, role: Optional[str] = None, seniority: Optional[str] = None, location: Optional[str] = None, requirements: Optional[List[str]] = None, responsibilities: Optional[List[str]] = None, benefits: Optional[List[str]] = None) -> Dict[str, Any]:
    prompt_context = {
        "company": company or "Company",
        "role": role or "Role",
        "seniority": seniority or "Senior",
        "location": location or "Remote",
        "requirements": requirements or ["3+ years experience", "Required tech stack"],
        "responsibilities": responsibilities or ["Key responsibility 1", "Key responsibility 2"],
        "benefits": benefits or ["Competitive salary", "Flexible schedule"],
    }
    return {"type": "content_prompt", "template": "job_post", "context": prompt_context}


def generate_application_form(position: Optional[str] = None, webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """Return a workflow trigger spec for creating an application form (n8n-ready)."""
    form_fields = [
        {"name": "full_name", "label": "Full Name", "type": "text", "required": True},
        {"name": "email", "label": "Email", "type": "email", "required": True},
        {"name": "resume_url", "label": "Resume URL", "type": "url", "required": True},
        {"name": "linkedin", "label": "LinkedIn", "type": "url", "required": False},
        {"name": "portfolio", "label": "Portfolio", "type": "url", "required": False},
    ]
    workflow = {
        "trigger": "webhook",
        "webhook_url": webhook_url or "${N8N_WEBHOOK_URL}",
        "steps": [
            {"action": "store_submission"},
            {"action": "notify_recruiter", "channel": "email"},
            {"action": "create_candidate_record"},
        ],
    }
    return {"type": "form_spec", "position": position or "Position", "fields": form_fields, "workflow": workflow}


def generate_quiz(role: Optional[str] = None, topics: Optional[List[str]] = None, num_questions: int = 10, difficulty: str = "medium") -> Dict[str, Any]:
    return {
        "type": "quiz_spec",
        "role": role or "Role",
        "difficulty": difficulty,
        "num_questions": num_questions,
        "topics": topics or ["Topic A", "Topic B"],
    }


def generate_homework(role: Optional[str] = None, objective: Optional[str] = None, deliverables: Optional[List[str]] = None, evaluation_rubric: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    return {
        "type": "homework_spec",
        "role": role or "Role",
        "objective": objective or "Build a small app demonstrating core skills",
        "deliverables": deliverables or ["GitHub repo", "README with instructions"],
        "evaluation_rubric": evaluation_rubric or {"correctness": 40, "code_quality": 30, "tests": 20, "docs": 10},
    }


def generate_candidate_journey(stages: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "type": "journey_spec",
        "stages": stages
        or [
            "Sourcing",
            "Application",
            "Screening",
            "Technical Assessment",
            "Onsite/Panel",
            "Offer",
            "Onboarding",
        ],
    }


def generate_funnel_report(time_range: str = "last_30_days", group_by: Optional[str] = None) -> Dict[str, Any]:
    return {
        "type": "funnel_report_request",
        "time_range": time_range,
        "group_by": group_by or "stage",
    }





