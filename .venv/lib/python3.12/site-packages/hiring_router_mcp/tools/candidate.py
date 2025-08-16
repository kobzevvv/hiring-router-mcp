from __future__ import annotations

from typing import Any, Dict, List, Optional


def candidate_assistant(task_description: str, stage: Optional[str] = None) -> Dict[str, Any]:
    return {
        "type": "assistant_guidance",
        "stage": stage or "general",
        "next_steps": [
            "Clarify target roles and locations",
            "Update resume with quantifiable impact",
            "Apply to curated list of companies",
        ],
        "task_description": task_description,
    }


def resume_optimizer(resume_text: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
    return {
        "type": "resume_prompt",
        "target_role": target_role or "Role",
        "instructions": [
            "Rewrite resume to be ATS-friendly",
            "Use action verbs and measurable outcomes",
            "Match keywords from job postings",
        ],
        "resume_text": resume_text or "",
    }


def interview_prep(role: Optional[str] = None, topics: Optional[List[str]] = None, days_until_interview: Optional[int] = None) -> Dict[str, Any]:
    return {
        "type": "interview_plan",
        "role": role or "Role",
        "topics": topics or ["Behavioral", "System Design", "Algorithms"],
        "schedule": [
            {"day": 1, "focus": "Behavioral stories (STAR)"},
            {"day": 2, "focus": "Core algorithms & DS"},
            {"day": 3, "focus": "System design walkthroughs"},
        ],
        "days_until_interview": days_until_interview,
    }


def salary_research(role: Optional[str] = None, location: Optional[str] = None, experience_years: Optional[int] = None) -> Dict[str, Any]:
    return {
        "type": "salary_research",
        "instructions": [
            "Use hh.ru and other sources to find salary ranges",
            "Record median, p25, p75",
            "Adjust for experience and company size",
        ],
        "role": role or "Role",
        "location": location or "Location",
    }





