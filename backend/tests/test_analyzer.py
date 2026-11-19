"""Unit tests for the framework-agnostic analyzer heuristics."""
from __future__ import annotations

import pytest

from backend.app.analyzer import (
    _build_checklist,
    _build_questions,
    _level_from_score,
    _score_risk,
    analyze_task,
)
from backend.app.models import AnalyzeResponse, RiskLevel


def test_low_risk_simple_task() -> None:
    result = analyze_task("Update the README with a short getting-started section for users.")
    assert isinstance(result, AnalyzeResponse)
    assert result.risk_level == RiskLevel.LOW
    assert result.risk_score < 25


def test_medium_risk_task() -> None:
    result = analyze_task(
        "Add an async REST API endpoint that reads from the database and caches the JSON response."
    )
    assert result.risk_level == RiskLevel.MEDIUM
    assert 25 <= result.risk_score < 50


def test_high_risk_security_and_data_task() -> None:
    result = analyze_task(
        "Add OAuth login, store tokens, run a database migration and drop the legacy users schema."
    )
    assert result.risk_level == RiskLevel.HIGH
    assert result.risk_score >= 50


@pytest.mark.parametrize(
    "score,expected",
    [(0, RiskLevel.LOW), (24, RiskLevel.LOW), (25, RiskLevel.MEDIUM),
     (49, RiskLevel.MEDIUM), (50, RiskLevel.HIGH), (100, RiskLevel.HIGH)],
)
def test_level_from_score_boundaries(score: int, expected: RiskLevel) -> None:
    assert _level_from_score(score) == expected


def test_score_risk_matches_keywords() -> None:
    score, matched = _score_risk("Implement payment webhook with encryption.")
    assert score > 0
    assert "payment" in matched
    assert "webhook" in matched
    assert "encrypt" in matched


def test_score_is_capped_at_100() -> None:
    task = "auth oauth password token encrypt permission secret payment drop migration breaking"
    score, _ = _score_risk(task)
    assert score == 100


def test_short_task_gets_clarification_question() -> None:
    questions = _build_questions("Fix bug", [])
    assert any("expand" in q.lower() for q in questions)


def test_questions_never_empty() -> None:
    result = analyze_task("Rename a variable in a small helper module for clarity now.")
    assert len(result.unclear_questions) >= 1


def test_high_risk_checklist_has_rollback() -> None:
    checklist = _build_checklist(RiskLevel.HIGH)
    assert any("rollback" in item.lower() for item in checklist)


def test_response_lists_are_populated() -> None:
    result = analyze_task("Add OAuth login and store tokens in the database.")
    assert result.implementation_plan
    assert result.suggested_tests
    assert result.pr_checklist
