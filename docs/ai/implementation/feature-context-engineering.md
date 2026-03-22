---
phase: implementation
title: Implementation — context-engineering
description: Implementation notes for DSPy summarization and deduplicated context files
feature: context-engineering
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Install dependencies from `pyproject.toml`; configure DSPy LM as for other promptymization modules.
- Use `resources/data` paths relative to package/project root consistently.

## Code Structure
**How is the code organized?**

- **`auto_prompt.promptymization`:** DSPy signatures and modules (`TextSummarizer`, `DeduplicatePromptSection`, `PromptMethodsContext`).
- **`auto_prompt.preprocessing`:** shared text/Markdown helpers (`HtmlPreprocessor.split_on_headers`, etc.).

## Implementation Notes
**Key technical details to remember:**

### Core Features
- **Summarization:** Output must be parseable into sections (headers + body) for dedupe.
- **Deduplication:** Reference file grows as novel content is merged; avoid re-processing unchanged sources if optimization added later.
- **Output:** Never overwrite existing context files without explicit flag; align with “new file per run” if that remains the rule.

### Patterns & Best Practices
- Classes with clear `forward` methods; Sphinx docstrings; tests mock `ChainOfThought` calls.

## Integration Points
**How do pieces connect?**

- **Upstream:** Markdown from scraper (`resources/data/**/page.md` or equivalent).
- **Downstream:** Agents read final context Markdown from `resources/data/context/` (or configured path).

## Error Handling
**How do we handle failures?**

- Invalid or empty Markdown: log and skip or produce empty contribution; do not crash whole pipeline unless configured.

## Performance Considerations
**How do we keep it fast?**

- Process files sequentially first; consider parallelism only after correctness.

## Security Notes
**What security measures are in place?**

- Context files are local; no PII logging from scraped content in production logs.
