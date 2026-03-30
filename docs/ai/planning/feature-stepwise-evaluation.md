---
phase: planning
title: Planning — stepwise-evaluation
description: Tasks for Braintrust integration, step registry, and first-step evals
feature: stepwise-evaluation
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [x] **M1:** Requirements reviewed (`/review-requirements`); **prompt-scorer** dependency direction locked (scorer → stepwise, Braintrust default).
- [x] **M2:** Design — **Braintrust SDK** as default; env vars in **`.env.example`**; fail-fast on misconfig for eval runs.
- [x] **M3:** Step registry + **context-engineering–invokable** eval path **in code** — package ``auto_prompt.evaluation``, ``PromptMethodsContext.build_context(emit_context_engineering_eval=…)``, CLI ``--eval`` / env ``AUTO_PROMPT_CONTEXT_EVAL``.
- [x] **M4:** Makefile ``build-context-eval``; ``tests/evaluation/`` with mocked ``init_logger``; CI uses same tests (no live Braintrust).

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [x] Task 1.1: **Braintrust** dependency (pinned in `pyproject.toml`) + :func:`load_braintrust_config_from_env`; **`.env.example`** lists ``BRAINTRUST_API_KEY``, optional project id/name.
- [x] Task 1.2: **`StepId`** + ``STEP_ORDER`` in ``evaluation/steps.py`` (`context_engineering` **first**, then scraper, agent, E2E).

### Phase 2: Core Features
- [x] Task 2.1: **EvalRecord** + **`log_step` / `run_step_eval`** + **`build_context_engineering_record`** — context pipeline calls after merge when eval enabled.
- [x] Task 2.2: **Observation import**: ``iter_observation_jsonl`` → :class:`EvalRecord` (JSONL → rows; Braintrust dataset push remains manual/UI for now).
- [x] Task 2.3: **End-to-end** placeholder: ``build_end_to_end_stub`` / ``EndToEndTraceStub`` in ``evaluation/end_to_end.py``.
- [x] Task 2.4: Add reusable contradiction-instruction scoring helper (``score_instruction_contradictions``) for scorer profiles and shared eval semantics.

### Phase 3: Integration & Polish
- [x] Task 3.1: **Makefile** ``build-context-eval``; CLI ``promptymize-build-context --eval`` / ``--eval-run-id``; env ``AUTO_PROMPT_CONTEXT_EVAL``.
- [x] Task 3.2: Tests with **mocked** ``init_logger`` in ``tests/evaluation/test_stepwise.py`` (no network).

## Dependencies
**What needs to happen in what order?**

- Stable **context** path: ``sources/data/context/prompt_methods_context.csv`` (**done** in context-engineering; model-type filtering supported by consumer helpers).
- **[x]** **`prompt-scorer`** calls this layer only—no duplicate Braintrust integration (see requirements).
- **context-engineering** **must** be able to call this layer when eval mode is on (**same** Braintrust client package as scorer path).

## Timeline & Estimates
**When will things be done?**

- First step eval is small; full step coverage grows with pipeline.

## Risks & Mitigation
**What could go wrong?**

- **API churn** on Braintrust SDK → pin versions; thin wrapper layer.
- **Flaky LLM outputs** → eval policies (tolerance, judge model) documented.

## Resources Needed
**What do we need to succeed?**

- Braintrust account and API access; sample project for dev.
