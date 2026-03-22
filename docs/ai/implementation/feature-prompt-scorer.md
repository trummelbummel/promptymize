---
phase: implementation
title: Implementation — prompt-scorer
description: Implementation notes for extensible scorers, context and dataset inputs, explanations
feature: prompt-scorer
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Add module under `auto_prompt` (exact package name TBD, e.g. `auto_prompt.scoring` or `auto_prompt.prompt_scorer`).
- Follow OO patterns used in `fact_extractor.py`; Sphinx docstrings for every public function/class.

## Code Structure
**How is the code organized?**

- `prompt_scorer.py` or package: `PromptScorer`, `ScoreResult`, `registry`, `scorers/` for built-ins and examples.
- Keep **scorer implementations** free of UI/agent code.

## Implementation Notes
**Key technical details to remember:**

### Core Features
- **Extensibility:** `register(name, scorer)` and/or decorator; document thread-safety if registry is global.
- **Context-only mode:** If `dataset is None`, scorers may use **only** context Markdown (summarized methods).
- **Dataset mode:** Pass structured examples; each scorer documents required fields.
- **Method selection:** `method_id` or similar selects a **section** or **evaluation profile**—implementation must match requirements doc once finalized.
- **Explanations:** Always set `explanation` (or structured `reasons: list[str]`) on `ScoreResult`.

### Patterns & Best Practices
- Prefer **composition** over deep inheritance; small scoring functions behind a common interface.
- Pure functions for deterministic metrics; isolate LLM calls in clearly named classes.

## Integration Points
**How do pieces connect?**

- **`prompt-optimizer-agent`:** imports `PromptScorer` or a thin `score_prompt_tool(...)` wrapper.

## Error Handling
**How do we handle failures?**

- Unknown `scorer_name` → clear `ValueError`.
- Missing context when scorer requires it → `ValueError` with message.
- Partial dataset rows → scorer-specific skip or fail (document per scorer).

## Performance Considerations
**How do we keep it fast?**

- Batch dataset evaluation where possible; cache parsed context file per process.

## Security Notes
**What security measures are in place?**

- Do not execute arbitrary code from dataset files; validate paths and formats.
