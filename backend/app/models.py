"""Pydantic v2 schemas shared by FastAPI and the MCP server."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalyzeRequest(BaseModel):
    """Incoming engineering task to analyze."""

    model_config = {"json_schema_extra": {
        "example": {"task": "Add OAuth login and store tokens in the DB."}
    }}

    task: str = Field(..., min_length=3, description="Engineering task description.")


class AnalyzeResponse(BaseModel):
    """Structured implementation guidance for a task."""

    risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100, description="0-100 heuristic score.")
    unclear_questions: list[str]
    implementation_plan: list[str]
    suggested_tests: list[str]
    pr_checklist: list[str]
