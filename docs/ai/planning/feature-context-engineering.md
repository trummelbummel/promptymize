---
phase: planning
title: Planning — context-engineering
description: Tasks and risks for DSPy summarization and deduplicated context generation
feature: context-engineering
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [x] **M1:** Requirements reviewed (`/review-requirements`).
- [x] **M2:** Design locked — merge into canonical context artifact with exact + optional LM dedupe.
- [x] **M3:** Implementation + tests for summarization + dedupe pipeline (``src/auto_prompt/promptymization/``).
- [x] **M4:** Optional manual smoke on real `sources/data` Markdown — covered by gated real-LLM integration test ``tests/promptymization/test_context_engineering_integration_llm.py`` when ``AUTO_PROMPT_RUN_REAL_INTEGRATION=1``.
- [x] **M5:** **Stepwise-evaluation** hook — ``build_context(emit_context_engineering_eval=…)``, CLI ``--eval`` / env ``AUTO_PROMPT_CONTEXT_EVAL`` (see **stepwise-evaluation** package).

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [x] Task 1.1: Inventory existing modules: `context_generation.py` (orchestrator), `dspy_modules` / ``PromptMethodSummarizer``, `DeduplicatePromptSection`.
- [x] Task 1.2: Canonical **output path** — ``sources/data/context/prompt_methods_context.csv`` (**merge-latest** into one file).

### Phase 2: Core Features
- [x] Task 2.1: Tighten **summarization signature** — ``SummarizePromptMethods`` in ``dspy_modules.py`` (structured instructions: ``##`` per method, bullet rules).
- [x] Task 2.2: Implement **orchestrator** — ``PromptMethodsContext`` in ``context_generation.py`` reads ``sources/data/**/*.md`` (excludes ``processed``/``context``), summarizes, moves folders to ``processed``, **merges** into canonical context rows at ``sources/data/context/prompt_methods_context.csv``.
- [x] Task 2.3: **Exact** deduplication via ``exact_dedupe_prompt_method_markdown`` (`dedupe_markdown.py`); optional **LM-assisted** incremental path via ``incremental_deduplicator`` constructor arg.
- [x] Task 2.4: Enforce **single-writer merge** via lock file (``sources/data/context/.prompt_methods_context.lock``) and timeout-based acquisition in ``PromptMethodsContext``.
- [x] Task 2.5: Publish context with **atomic replace** (write temp + ``fsync`` + rename) so readers never observe partial writes.
- [x] Task 2.6: Add **bounded input chunking** for long markdown sources (header-aware split + fallback slicing) with configurable limit (``max_chunk_chars``).
- [x] Task 2.7: Add **model-type labeling** + CSV row explosion (one method can emit multiple rows for different ``model_type`` values) for downstream filtering.

### Phase 3: Integration & Polish
- [x] Task 3.1: Run pipeline via ``make build-context`` or ``uv run auto-prompt-build-context`` (see ``cli.py``, ``pyproject.toml`` `[project.scripts]`).
- [x] Task 3.2: Tests — ``tests/promptymization/test_context_generation.py``, ``test_dedupe_markdown.py`` (mocked summarizer); extend when adding LM integration tests.
- [x] Task 3.3: Provide CSV context loader helpers (``context_csv.py``) so downstream consumers can filter by ``model_type`` and reconstruct filtered markdown context.

### Phase 4: Evaluation integration (with stepwise-evaluation)
- [x] Task 4.1: **Optional** eval mode on ``PromptMethodsContext.build_context`` + CLI (``--eval``, ``AUTO_PROMPT_CONTEXT_EVAL``) invoking ``auto_prompt.evaluation`` after merge.
- [x] Task 4.2: **EvalRecord** payloads via ``build_context_engineering_record`` (source paths, SHA-256, excerpt).
- [x] Task 4.3: **Fail-fast** via ``ConfigurationError`` when eval on but ``BRAINTRUST_API_KEY`` missing; default **off**.
- [x] Task 4.4: **tests/evaluation/** mocks Braintrust; no network in CI.

## Dependencies
**What needs to happen in what order?**

- Dedupe behavior depends on summarization output shape (headers/sections stable).
- Scraper feature (`prompt-method-scraper`) provides inputs but context-engineering can be tested with fixture `.md` files.
- **stepwise-evaluation** (Braintrust SDK + registry) is a **dependency for Phase 4** only; core merge pipeline stays usable without it.

## Timeline & Estimates
**When will things be done?**

- Dedupe + evaluation of duplicate detection often needs iteration; buffer for prompt tuning.

## Risks & Mitigation
**What could go wrong?**

- **Semantic duplicates** not caught by string equality → mitigate with LM signature or normalization.
- **Cost/latency** on large corpora → batching, caching intermediate summaries.

## Resources Needed
**What do we need to succeed?**

- DSPy + LM access; sample `sources/data` Markdown for integration smoke tests.
