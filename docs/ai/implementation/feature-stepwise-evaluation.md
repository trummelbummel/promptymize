---
phase: implementation
title: Implementation — stepwise-evaluation
description: Implementation notes for Braintrust, step hooks, and observation import
feature: stepwise-evaluation
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Install deps with `uv sync`; copy **`.env.example`** to `.env` and set **Braintrust** variables (**required** for eval runs); do not commit secrets.
- Follow `.cursor/rules/fact-extractor-format.mdc` for new Python modules.

## Code Structure
**How is the code organized?**

- Package: **`src/auto_prompt/evaluation/`** — `config.py` (env), `steps.py` (`StepId`), `records.py` (`EvalRecord`), `logging.py` (`log_step`, `build_context_engineering_record`), `observations.py` (`iter_observation_jsonl`), `end_to_end.py` (stub trace). Shared errors: **`src/auto_prompt/errors.py`**.
- Step-specific hooks should be **thin**; heavy logic stays in existing **context-engineering** / **scraper** modules.

## Implementation Notes
**Key technical details to remember:**

### Core Features
- **Wrapper**: centralize Braintrust client creation and error handling.
- **Step hooks**: call logging only when eval mode enabled (env or CLI flag)—**including** hooks invoked from **context-engineering** (`context_engineering` **first** in registry).
- **Observations**: JSONL via ``iter_observation_jsonl`` — one object per line with ``step_id``, ``run_id``, ``inputs``, ``outputs`` (optional ``labels``, ``notes``, ``metadata``).

### Patterns & Best Practices
- Never log raw secrets; **truncate** long prompts if Braintrust limits apply.

## Integration Points
**How do pieces connect?**

- **context-engineering:** ``PromptMethodsContext.build_context(emit_context_engineering_eval=True)`` or CLI ``promptymize-build-context --eval`` / ``AUTO_PROMPT_CONTEXT_EVAL=1`` — after write, calls ``log_step`` with ``build_context_engineering_record``. **Do not** require Braintrust when eval mode is off.
- **prompt-scorer:** **depends on** this package for Braintrust runs; implements prompt/compare API only—**no** parallel Braintrust client.

## Error Handling
**How do we handle failures?**

- **Eval runs:** missing or invalid **Braintrust** configuration → **fail fast** with a clear error (no silent skip in production).
- **Non-eval pipelines** (e.g. context build without logging): do not require Braintrust; only flows that invoke stepwise-evaluation need credentials.

## Performance Considerations
**How do we keep it fast?**

- Batch rows where Braintrust supports batch insert.

## Security Notes
**What security measures are in place?**

- API keys via env; document redaction for customer prompts in shared Braintrust projects.
