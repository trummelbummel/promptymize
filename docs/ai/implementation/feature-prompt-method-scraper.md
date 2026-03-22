---
phase: implementation
title: Implementation — prompt-method-scraper
description: Implementation notes for config-driven scraping to resources/data
feature: prompt-method-scraper
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Install project deps per `pyproject.toml` / `Makefile`.
- Point scraper at `auto-prompt/scraper_targets.yaml` (or configured path).

## Code Structure
**How is the code organized?**

- Prefer extending `auto_prompt.scraper` modules (`config`, `fetch`, `web_scraper`, `writer`, `paths`) rather than new top-level packages unless necessary.
- `resources/data` layout must match design doc once finalized.

## Implementation Notes
**Key technical details to remember:**

### Core Features
- **Config:** Load targets from YAML; validate `folder_name` and non-empty URL lists.
- **Storage:** Write Markdown under `resources/data/<folder_name>/...` per design.
- **arXiv / PDF:** Implement in dedicated helpers to keep single responsibility.

### Patterns & Best Practices
- Object-oriented style consistent with existing scraper code.
- Sphinx-style docstrings on new/changed public methods.

## Integration Points
**How do pieces connect?**

- Downstream: `promptymization` / `PromptMethodsContext` expects Markdown under `resources/data`.

## Error Handling
**How do we handle failures?**

- Per-URL errors should not silently skip without log; define whether to fail fast or continue.

## Performance Considerations
**How do we keep it fast?**

- Optional parallel fetches later; start sequential for simplicity.

## Security Notes
**What security measures are in place?**

- Do not log full request bodies with secrets; validate URLs before fetch where practical.
