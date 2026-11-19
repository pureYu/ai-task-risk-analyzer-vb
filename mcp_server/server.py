"""MCP server exposing the task risk analyzer as a tool.

Thin wrapper around `analyze_task()` — no analysis logic lives here. Any MCP
client (e.g. VS Code / GitHub Copilot Agent Mode) can call the `analyze_task`
tool to get structured risk guidance for an engineering task.

Run with:
    python -m mcp_server.server
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running as a standalone script (`python mcp_server/server.py`) by
# ensuring the project root is importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP

from backend.app.analyzer import analyze_task
from backend.app.models import AnalyzeResponse
from backend.app.telemetry import setup_telemetry

setup_telemetry()

mcp = FastMCP("ai-task-risk-analyzer")


@mcp.tool()
def analyze_engineering_task(task: str) -> AnalyzeResponse:
    """Analyze an engineering task and return structured SDLC guidance.

    Args:
        task: A free-text description of the engineering task to analyze.

    Returns:
        Structured guidance with a risk level/score, clarifying questions,
        an implementation plan, suggested tests and a PR checklist.
    """
    return analyze_task(task)


if __name__ == "__main__":
    mcp.run()
