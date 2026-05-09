# AGENTS.md
# This file is injected into the system prompt at the start of every agent session.
# DRY principle: common agent rules are managed in one place.

## Role Principles
- You perform only the single role you have been assigned (SRP).
- Requests outside your role scope are delegated to the appropriate agent.

## Architecture Rules
- No direct database access — always go through the Repository layer
- External service calls must only be made through the tools/ layer
- No hardcoding of environment variables or config values in code

## Action Classification
- GREEN (auto-executable): reads, queries, analysis
- YELLOW (audit log required): file creation, data modification
- RED (human approval required): deletion, email/Slack sending, payments

## Absolutely Forbidden Actions
- Using `rm -rf`, `DROP TABLE`, `DELETE FROM` (without WHERE)
- Directly modifying production environment variables
- Sending data externally without approval

## Execution Principles
- Always write a plan (Todo) before starting a long-running task
- Confirm with a human before taking any irreversible action
- When uncertain, do not act — ask a clarifying question instead
