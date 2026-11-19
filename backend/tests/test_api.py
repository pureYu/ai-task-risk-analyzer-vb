"""Integration tests for the FastAPI endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_full_schema() -> None:
    response = client.post("/analyze", json={"task": "Add OAuth login and store tokens in the DB."})
    assert response.status_code == 200
    body = response.json()
    for key in (
        "risk_level",
        "risk_score",
        "unclear_questions",
        "implementation_plan",
        "suggested_tests",
        "pr_checklist",
    ):
        assert key in body
    assert body["risk_level"] in ("low", "medium", "high")


def test_analyze_rejects_too_short_task() -> None:
    response = client.post("/analyze", json={"task": "x"})
    assert response.status_code == 422


def test_analyze_requires_task_field() -> None:
    response = client.post("/analyze", json={})
    assert response.status_code == 422


@pytest.mark.parametrize(
    "task,expected_level",
    [
        ("Update the README with a short getting-started section for users.", "low"),
        ("Add OAuth login, run a database migration and drop the users schema.", "high"),
    ],
)
def test_analyze_risk_levels(task: str, expected_level: str) -> None:
    response = client.post("/analyze", json={"task": task})
    assert response.status_code == 200
    assert response.json()["risk_level"] == expected_level
