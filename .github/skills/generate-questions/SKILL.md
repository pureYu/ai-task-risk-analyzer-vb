---
name: generate-questions
description: 'Generate the clarifying questions that must be answered before implementing a task, so requirements and edge cases are nailed down first. USE WHEN a task is vague, or before starting non-trivial implementation.'
---

# Skill: Generate Clarifying Questions

Produce the smallest set of high-leverage questions that unblock implementation.

## Inputs
- A free-text engineering task description.

## Method
1. Identify ambiguous scope, missing acceptance criteria and hidden assumptions.
2. Ask targeted questions per risk area when relevant:
   - **Auth/secrets**: which provider/flow, where are secrets stored?
   - **Data**: is a migration needed, what is the rollback plan?
   - **Integration**: which external service and version, failure handling?
   - **Concurrency**: expected throughput and concurrency limits?
   - **Non-functional**: performance, security, SLAs, observability?
3. Always include at least one question; if the task is short, ask for concrete
   scope and constraints.

## Output
- A bulleted list of clarifying questions, ordered by how much they reduce risk.
- Keep them specific and answerable — avoid generic or rhetorical questions.
