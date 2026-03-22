---
phase: implementation
title: Implementation — prompt-optimizer-agent
description: Implementation notes for CO-STAR flow, proposals, apply step, and scorer calls
feature: prompt-optimizer-agent
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Follow project Python/DSPy conventions; align with **`prompt-scorer`** package or module once implemented.
- Use test doubles for LLM and scorer in unit tests.

## Code Structure
**How is the code organized?**

- Prefer a dedicated package or module e.g. `auto_prompt.agent` or `auto_prompt.prompt_optimizer` (exact name TBD with repo layout).
- Keep **tool boundary** to **`prompt-scorer`** in one adapter class for easy mocking.

## Implementation Notes
**Key technical details to remember:**

### Core Features
- **CO-STAR:** Store six optional slots + free-text “task description” as required by product; map to internal schema.
- **Proposals:** Pass context + user state into DSPy module(s); output structured proposal IDs or method names from context sections.
- **Apply:** Single function `apply_proposal(user_prompt, proposal) -> str` for testability.
- **Scoring:** `score_prompt(prompt, phase)` calling **`prompt-scorer`**; never duplicate scoring logic here.

### Patterns & Best Practices
- OO style consistent with `fact_extractor.py`; Sphinx docstrings; early returns for empty inputs.

## Integration Points
**How do pieces connect?**

- Reads **context-engineering** output path from config or constructor.
- Delegates scoring to **`prompt-scorer`** tool only.

## Error Handling
**How do we handle failures?**

- Missing context: degrade to generic suggestions only if explicitly allowed; otherwise inform user.
- Scorer failure: surface error; optionally skip post-score with user consent.

## Performance Considerations
**How do we keep it fast?**

- Cache context file read per session; avoid re-scoring identical prompt text.

## Security Notes
**What security measures are in place?**

- Do not exfiltrate user prompts to third parties beyond configured LM/scorer endpoints.
