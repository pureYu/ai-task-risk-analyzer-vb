"""FastAPI app exposing the task risk analyzer.

Thin wrapper around `analyze_task()`; contains no analysis logic itself.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .analyzer import analyze_task
from .models import AnalyzeRequest, AnalyzeResponse
from .telemetry import setup_telemetry

setup_telemetry()

app = FastAPI(
    title="AI Task Risk Analyzer",
    description="Analyzes engineering tasks and returns risk, questions, plan, "
    "tests and a PR checklist.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FastAPIInstrumentor.instrument_app(app)

_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a task description and return structured guidance."""
    return analyze_task(request.task)


if _FRONTEND_DIR.exists():
    @app.get("/")
    async def index() -> FileResponse:
        """Serve the single-page frontend."""
        return FileResponse(_FRONTEND_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")
