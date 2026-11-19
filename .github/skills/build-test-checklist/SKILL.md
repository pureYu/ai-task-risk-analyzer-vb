---
name: build-test-checklist
description: 'Derive a test strategy and a pre-PR checklist from a task and its risk profile, so coverage and quality gates are defined before coding. USE WHEN planning tests for a change or preparing to open a pull request.'
---

# Skill: Build Test & PR Checklist

Turn a task and its risk level into a concrete test plan and PR checklist.

## Inputs
- A task description and (optionally) its risk level/score.

## Method
1. Start from the universal baseline tests:
   - Happy-path for the primary scenario.
   - Input validation / boundary cases.
   - Error handling for invalid or missing input.
2. Add risk-specific tests:
   - **Auth**: unauthorized + expired-credential access.
   - **Data**: migration up/down + data-integrity.
   - **Concurrency**: race conditions / idempotency.
   - **Integration**: external failure, retry/timeout.
3. Build the PR checklist, escalating with risk:
   - Always: tests pass, no secrets committed, typed & documented public APIs,
     errors handled/logged, clear PR description.
   - Medium/High: peer security/data-impact review.
   - High: documented rollback / feature-flag strategy.

## Output
- A `suggested_tests` bullet list mapped to the relevant risks.
- A `pr_checklist` bullet list appropriate to the risk level.
