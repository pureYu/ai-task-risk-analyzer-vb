---
mode: agent
description: 'Analyze an engineering task before coding: risk, clarifying questions, implementation plan, tests and PR checklist.'
tools: ['codebase', 'search', 'ai-task-risk-analyzer']
---

# Analyze Task Before Coding

Analyze the following engineering task **before any implementation begins**.

Task:
> ${input:task:Describe the engineering task to analyze}

Steps:
1. Call the `analyze_engineering_task` MCP tool (server `ai-task-risk-analyzer`)
   to get the structured baseline.
2. Search the workspace for any files/modules this task would touch and refine
   the plan with that context.
3. Respond with these sections, concise and actionable:
   - **Risk** — level + score with a one-line reason.
   - **Resolve first** — clarifying questions that block implementation.
   - **Implementation plan** — small, ordered, reviewable steps.
   - **Test strategy** — suggested tests mapped to risks.
   - **PR checklist** — what must be true before opening a PR.

Do **not** write feature code until the high-risk questions are answered.
