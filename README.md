# 🛡️ Agentic SDLC Assistant: AI Task Risk Analyzer

A small Python service that analyzes an engineering **task description** and returns
structured guidance **before you start coding** — so requirements, risks, edge cases
and test strategy are clear up front.

It returns:
- **`risk_level`**: `low` | `medium` | `high` (+ a 0–100 score)
- **`unclear_questions`**: what to clarify first
- **`implementation_plan`**: ordered, reviewable steps
- **`suggested_tests`**: test cases mapped to risks
- **`pr_checklist`**: gates before opening a PR

It is exposed as a **FastAPI** HTTP API **and** an **MCP server**, and is observable
end-to-end with **OpenTelemetry** (console exporter by default, OTLP/Jaeger optional).

## Architecture

```
ai-task-risk-analyzer/
├── .github/
│   ├── copilot-instructions.md   # global Copilot context
│   ├── agents/                   # risk-analyzer agent (Agent Mode)
│   ├── skills/                   # analyze-risk, generate-questions, build-test-checklist
│   └── prompts/                  # analyze-task reusable prompt
├── .vscode/mcp.json              # MCP server registration for VS Code
├── backend/app/
│   ├── analyzer.py               # framework-agnostic core logic (single source of truth)
│   ├── models.py                 # Pydantic v2 schemas
│   ├── telemetry.py              # OpenTelemetry setup
│   └── main.py                   # FastAPI wrapper (POST /analyze)
├── backend/tests/                # pytest suite
├── frontend/index.html           # Alpine.js single-page UI (no build step)
├── mcp_server/server.py          # MCP wrapper around analyze_task()
├── Dockerfile                    # backend image (API + frontend)
└── docker-compose.yml            # backend + Jaeger, one command up
```

**Key rule:** all analysis logic lives in `backend/app/analyzer.py`. FastAPI and the
MCP server are thin wrappers that call the same `analyze_task()` — no duplication.

## Quick start with Docker (recommended)

Runs the API, web UI and **Jaeger** tracing with a single command. Requires
[Docker Desktop](https://www.docker.com/products/docker-desktop/) to be installed
and running.

```bat
docker compose up --build
```

Then open:

- **Web UI + API**: http://localhost:8000/
- **API docs**: http://localhost:8000/docs
- **Jaeger UI**: http://localhost:16686/ (search for service `ai-task-risk-analyzer`)

The backend is wired to Jaeger via `OTEL_EXPORTER_OTLP_ENDPOINT`, so every request
shows up as a distributed trace in the Jaeger UI.

Stop and remove the containers:

```bat
docker compose down
```

> Re-run `docker compose up --build` after changing code or dependencies, since the
> source is baked into the image at build time.

## Local setup (without Docker)

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the API + web UI

```bat
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

- Web UI: http://127.0.0.1:8000/
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Each request emits an OpenTelemetry trace to the console, with a child
`analyze_task` span carrying `risk.level`, `risk.score` and `questions.count`.

### Optional: export traces to Jaeger

```bat
set OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
.venv\Scripts\python.exe -m uvicorn backend.app.main:app
```

## How to use

### Web UI

Open http://localhost:8000/, paste an engineering task description, and submit. The
page renders the risk level and score, clarifying questions, the implementation plan,
suggested tests and a PR checklist.

### HTTP API

Send a `POST /analyze` request with a JSON body containing the `task` text:

```bat
curl -X POST http://localhost:8000/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"task\": \"Add OAuth login and store refresh tokens in the database\"}"
```

Response shape:

```json
{
  "risk_level": "high",
  "risk_score": 72,
  "unclear_questions": ["..."],
  "implementation_plan": ["..."],
  "suggested_tests": ["..."],
  "pr_checklist": ["..."]
}
```

Explore and try endpoints interactively at http://localhost:8000/docs.

## Run the tests

```bat
.venv\Scripts\python.exe -m pytest
```

## MCP server

Registered in `.vscode/mcp.json`. In VS Code: **MCP: List Servers** →
start `ai-task-risk-analyzer`, then ask Copilot Agent Mode to analyze a task.

Run it standalone:

```bat
set PYTHONPATH=%CD%
.venv\Scripts\python.exe -m mcp_server.server
```

## Copilot customization

- **Instructions** (`.github/copilot-instructions.md`) ground every interaction.
- **Agent** (`.github/agents/risk-analyzer.agent.md`) drives the analyze-before-code flow.
- **Skills** (`.github/skills/*/SKILL.md`) package the risk, questions and test-checklist logic.
- **Prompt** (`.github/prompts/analyze-task.prompt.md`) is a one-shot entry point.
