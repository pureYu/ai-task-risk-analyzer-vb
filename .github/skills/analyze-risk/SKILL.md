---
name: analyze-risk
description: 'Assess the risk level of an engineering task (low/medium/high) by weighing security, data, integration and concurrency factors. USE WHEN the user asks how risky a change is, or before planning implementation of a non-trivial task.'
---

# Skill: Analyze Risk

Estimate the risk of an engineering task and explain the drivers.

## Inputs
- A free-text engineering task description.

## Method
1. If the `ai-task-risk-analyzer` MCP server is available, call
   `analyze_engineering_task` and use its `risk_level` / `risk_score` as the
   baseline.
2. Otherwise score heuristically. Raise risk for:
   - **Security**: auth, OAuth, tokens, secrets, encryption, permissions.
   - **Data**: database migrations, schema changes, deletes/drops.
   - **Integration**: payments, third-party APIs, webhooks.
   - **Concurrency/scale**: async, race conditions, queues, caching.
   - **Breaking changes**: deprecations, public-contract changes.
3. Treat very short / vague tasks as under-specified (adds uncertainty).

## Output
- `risk_level`: `low` | `medium` | `high`
- A one-line justification naming the top 1-3 risk drivers.
- A recommendation: proceed, clarify first, or request a design review (high).
