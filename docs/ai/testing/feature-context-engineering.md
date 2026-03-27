---
phase: testing
title: Testing — context-engineering
description: Test strategy for DSPy summarization and deduplicated context output
feature: context-engineering
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- **Core logic:** summarizer section/header extraction, dedupe module with mocked LM predictions, orchestrator path resolution.
- Mirror `tests/` structure to `src/` per project rules.

## Unit Tests
**What individual components need testing?**

### ``PromptMethodSummarizer`` / summarization module
- [ ] `forward` returns `summary`, `headers`, `sections` with expected splitting (existing tests; extend if behavior changes).
- [ ] Empty input / empty summary edge cases.

### DeduplicatePromptSection
- [ ] No match → full section retained.
- [ ] Match → only novel bullets.
- [ ] All duplicates → empty contribution.
- [ ] Multiple sections mixed scenario.

### PromptMethodsContext (or orchestrator)
- [ ] Creates `processed` / `context` dirs as designed.
- [ ] **Merge-latest** into ``prompt_methods_context.csv`` with lock + atomic replace (see design).
- [ ] Moves processed folders only once per run (if behavior unchanged).
- [ ] **Eval mode off:** no Braintrust client imports or network.
- [ ] **Eval mode on (mocked):** asserts stepwise called once per successful build with ``context_engineering`` StepId.

## Integration Tests
**How do we test component interactions?**

- [ ] Temporary directory with fake `sources/data` tree and two `.md` files → single aggregated context file content assertions (mock summarizer/dedupe if needed).

## End-to-End Tests
**What user flows need validation?**

- [ ] Optional: full pipeline with recorded LM outputs (heavy; usually skipped in CI).

## Test Data
**What data do we use for testing?**

- Small Markdown strings with duplicate headers/bullets; synthetic “reference” vs “new” text.

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Standard `make test` when environment supports builds.

## Manual Testing
**What requires human validation?**

- Read final merged context CSV and per-method files for clarity and lack of obvious duplicates.

## Performance Testing
**How do we validate performance?**

- Optional timing on large folder trees.

## Bug Tracking
**How do we manage issues?**

- Track false positives/negatives in dedupe as quality issues, not always “bugs.”
