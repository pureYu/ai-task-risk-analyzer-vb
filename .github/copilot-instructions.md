# Copilot Instructions — Agentic SDLC Assistant: AI Task Risk Analyzer

## Project Purpose
A Python mini-service that analyzes an engineering **task description** and returns:
- `risk_level`: `low` | `medium` | `high`
- `unclear_questions`: clarifying questions to ask before coding
- `implementation_plan`: ordered, actionable steps
- `suggested_tests`: test cases to cover
- `pr_checklist`: items to verify before opening a PR

It is observable end-to-end via OpenTelemetry (APM) and exposed both as a
FastAPI HTTP API and an MCP server.

## Tech Stack
- **Backend**: FastAPI + Uvicorn, Pydantic v2
- **Telemetry**: OpenTelemetry SDK, console exporter (Jaeger optional)
- **MCP**: official `mcp` Python SDK
- **Frontend**: single `index.html` using Alpine.js (CDN, no build step)
- **Tests**: pytest
- **Python**: 3.11+

## Architecture Rules
- Core analysis logic lives in `backend/app/analyzer.py` and is **framework-agnostic**.
- FastAPI (`main.py`) and the MCP server (`mcp/server.py`) are thin wrappers that
  call the same `analyze_task()` function. **Never duplicate logic.**
- All public functions are typed and use Pydantic models from `backend/app/models.py`.
- Every analysis call must run inside an OpenTelemetry span with attributes:
  `task.length`, `risk.level`, `questions.count`.

## Coding Conventions
- Use Pydantic v2 (`model_config`, `Field`) — not v1 syntax.
- Async FastAPI route handlers.
- Type hints everywhere; no bare `dict` returns from public functions.
- Small, pure functions for scoring heuristics so they are unit-testable.
- Docstrings on public functions describing inputs/outputs.

## Testing Conventions
- Tests in `backend/tests/`, named `test_*.py`.
- Use `pytest` fixtures; avoid network calls.
- Cover each risk level (low/medium/high) with at least one case.

## Definition of Done
- Endpoint `POST /analyze` returns the full response schema.
- A trace is emitted to the console for each request.
- `pytest` passes.
- `index.html` can call the API and render results.
