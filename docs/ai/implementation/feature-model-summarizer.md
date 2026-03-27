---
phase: implementation
title: Implementation — model-summarizer
description: Implementation notes for benchmark/task mapping and post-training summaries
feature: model-summarizer
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Reuse existing project Python patterns (small modules, explicit data models, test-first where possible).
- Keep fetchers deterministic in tests by mocking network calls.

## Code Structure
**How is the code organized?**

- Suggested package layout:
  - `auto_prompt/model_summarizer/model_sources.py` — Hugging Face + optional public source fetchers
  - `auto_prompt/model_summarizer/benchmark_registry.py` — benchmark → task mapping table
  - `auto_prompt/model_summarizer/extractors.py` — parse benchmark/post-training evidence
  - `auto_prompt/model_summarizer/summarizer.py` — merge evidence and produce output model
  - `auto_prompt/model_summarizer/types.py` — typed dataclasses/TypedDicts for outputs

## Implementation Notes
**Key technical details to remember:**

### Core Features
- **Model id validation:** accept Hugging Face style `org/model_name`; reject empty/invalid values with `ValidationError`.
- **Source retrieval:** fetch model card text + metadata from Hugging Face first; add optional secondary sources only when they improve coverage.
- **Benchmark extraction:** parse benchmark names/scores and preserve source URL and raw notes.
- **Task mapping:** map benchmark identifiers to task labels using a curated registry (fallback to `"unknown_task"` with explanation when not mapped).
- **Post-training extraction:** detect and normalize methods (e.g. instruction tuning, RLHF, DPO, safety tuning, tool-use training) with evidence snippets.
- **Summary synthesis:** produce:
  - structured JSON (`ModelSummary`),
  - markdown summary of strengths, limitations, and unknowns.

### Patterns & Best Practices
- Prefer explicit typed objects over loose dicts at module boundaries.
- Keep extraction functions pure; isolate network I/O in source modules.
- Preserve traceability by attaching source URLs for every benchmark/post-training claim.

## Integration Points
**How do pieces connect?**

- Optional REST backend route:
  - `POST /v1/models/{model_id}/summary`
  - returns serialized `ModelSummary` for UI consumption.
- Optional UI integration:
  - benchmark table with task labels,
  - post-training badges/sections,
  - strengths/limitations summary panel.

## Error Handling
**How do we handle failures?**

- `ValidationError` for invalid model id.
- `ResourceNotFoundError` when model or required evidence is not found.
- `DependencyUnavailableError` for upstream source/network failures.
- Return partial evidence only when policy explicitly allows; always report unknowns.

## Performance Considerations
**How do we keep it fast?**

- Bound request timeouts per source.
- Consider source-level caching keyed by model id + timestamp window.
- Avoid repeated parsing of identical model cards in one request.

## Security Notes
**What security measures are in place?**

- Only fetch from allowed public domains/providers (e.g. Hugging Face and approved sources).
- Do not execute arbitrary content from model cards/pages.
- Sanitize source text before logging; avoid leaking sensitive runtime config.

