"""Framework-agnostic task analysis logic.

FastAPI and the MCP server both call `analyze_task()`. No logic is duplicated.
"""
from __future__ import annotations

from opentelemetry import trace

from .models import AnalyzeResponse, RiskLevel

tracer = trace.get_tracer(__name__)

# Keywords that raise the risk score (weight per category).
# Use root/stem forms so that e.g. "migrate" matches "migration" patterns.
_RISK_KEYWORDS: dict[str, int] = {
    # security-sensitive
    "auth": 20, "oauth": 20, "password": 20, "token": 15, "encrypt": 15,
    "permission": 15, "secret": 20,
    # data / persistence — include verb stems so "migrate" matches like "migration"
    "database": 10, "migrat": 20, "schema": 15, "delete": 15, "drop": 25,
    "alter table": 20, "column": 10, "index": 8, "backfill": 15, "seed": 8,
    # integration / external
    "payment": 25, "api": 8, "webhook": 10, "third-party": 12, "integration": 10,
    # concurrency / scale
    "async": 10, "concurrency": 15, "race": 20, "queue": 10, "cache": 8,
    # breaking
    "breaking": 25, "deprecate": 15, "refactor": 8,
}

# Vague terms that imply unclear requirements.
_VAGUE_TERMS = ("etc", "and so on", "somehow", "maybe", "tbd", "improve",
                "optimize", "handle", "support")


def _score_risk(task: str) -> tuple[int, list[str]]:
    """Return (0-100 score, matched keywords) for a task string."""
    lowered = task.lower()
    score = 0
    matched: list[str] = []
    for keyword, weight in _RISK_KEYWORDS.items():
        if keyword in lowered:
            score += weight
            matched.append(keyword)
    # Short tasks are under-specified -> add uncertainty.
    if len(task.split()) < 8:
        score += 10
    return min(score, 100), matched


def _level_from_score(score: int) -> RiskLevel:
    if score >= 50:
        return RiskLevel.HIGH
    if score >= 25:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _build_questions(task: str, matched: list[str]) -> list[str]:
    lowered = task.lower()
    questions: list[str] = []
    if any(k in matched for k in ("auth", "oauth", "token", "secret", "password")):
        questions.append("Which auth provider/flow is required, and where are secrets stored?")
    if any(k in matched for k in ("database", "migrat", "schema", "drop", "delete", "alter table", "column", "backfill")):
        questions.append("Is a data migration needed, and what is the rollback plan?")
    if any(k in matched for k in ("payment", "third-party", "webhook", "integration")):
        questions.append("Which external service and version is the integration target?")
    if any(k in matched for k in ("async", "concurrency", "race", "queue")):
        questions.append("What are the expected throughput and concurrency limits?")
    if any(term in lowered for term in _VAGUE_TERMS):
        questions.append("Some requirements are vague — can you define the exact acceptance criteria?")
    if len(task.split()) < 8:
        questions.append("Can you expand the task with concrete scope and constraints?")
    if not questions:
        questions.append("Are there any non-functional requirements (performance, security, SLAs)?")
    return questions


def _build_plan(level: RiskLevel, matched: list[str]) -> list[str]:
    plan = ["Clarify open questions and confirm acceptance criteria.",
            "Break the task into small, reviewable units."]
    if any(k in matched for k in ("database", "migrat", "schema", "alter table", "column", "backfill")):
        plan.append("Design schema/migration with a forward and rollback path.")
    if any(k in matched for k in ("auth", "oauth", "token", "secret")):
        plan.append("Implement auth using vetted libraries; keep secrets in config/vault.")
    if any(k in matched for k in ("api", "integration", "webhook", "third-party")):
        plan.append("Define request/response contracts and handle external failures.")
    plan.append("Add tests alongside implementation (TDD where practical).")
    if level == RiskLevel.HIGH:
        plan.append("Request an early design review before merging.")
    plan.append("Open a small PR with a clear description and checklist.")
    return plan


def _build_tests(matched: list[str]) -> list[str]:
    tests = ["Happy-path test for the primary scenario.",
             "Input validation / boundary tests.",
             "Error-handling test for invalid or missing input."]
    if any(k in matched for k in ("auth", "oauth", "token", "permission")):
        tests.append("Unauthorized and expired-credential access tests.")
    if any(k in matched for k in ("database", "migrat", "schema", "delete", "column", "backfill")):
        tests.append("Migration up/down and data-integrity test.")
    if any(k in matched for k in ("async", "concurrency", "race", "queue")):
        tests.append("Concurrency test for race conditions / idempotency.")
    if any(k in matched for k in ("payment", "integration", "webhook")):
        tests.append("External-service failure and retry/timeout test.")
    return tests


def _build_checklist(level: RiskLevel) -> list[str]:
    checklist = [
        "Code is covered by tests and all tests pass.",
        "No secrets or credentials committed.",
        "Public functions are typed and documented.",
        "Errors are handled and logged.",
        "PR description explains the change and trade-offs.",
    ]
    if level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
        checklist.append("Security/data-impact reviewed by a peer.")
    if level == RiskLevel.HIGH:
        checklist.append("Rollback / feature-flag strategy documented.")
    return checklist


def analyze_task(task: str) -> AnalyzeResponse:
    """Analyze an engineering task and return structured guidance.

    Wrapped in an OpenTelemetry span exposing task length, risk level and
    question count so the call is observable in APM.
    """
    with tracer.start_as_current_span("analyze_task") as span:
        score, matched = _score_risk(task)
        level = _level_from_score(score)
        questions = _build_questions(task, matched)

        span.set_attribute("task.length", len(task))
        span.set_attribute("task.matched_keywords", ", ".join(matched))
        span.set_attribute("risk.level", level.value)
        span.set_attribute("risk.score", score)
        span.set_attribute("questions.count", len(questions))

        return AnalyzeResponse(
            risk_level=level,
            risk_score=score,
            unclear_questions=questions,
            implementation_plan=_build_plan(level, matched),
            suggested_tests=_build_tests(matched),
            pr_checklist=_build_checklist(level),
        )
