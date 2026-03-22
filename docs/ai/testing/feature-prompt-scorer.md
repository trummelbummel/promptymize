---
phase: testing
title: Testing — prompt-scorer
description: Tests for registry, context-only and dataset modes, comparison, and explanations
feature: prompt-scorer
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- **Core:** registry, dispatch, `ScoreResult` shape, `compare` deltas.
- **Modes:** context-only (no dataset) and dataset present (mocked or tiny fixture).
- **Explanations:** non-empty for built-ins or explicit documented exception.

## Unit Tests
**What individual components need testing?**

### Registry / facade
- [ ] Register and retrieve custom scorer.
- [ ] Unknown scorer name raises.

### Scoring functions (deterministic)
- [ ] Context-only scorer returns stable scores for fixed prompt + context fixture.
- [ ] Dataset scorer consumes minimal CSV/JSON fixture.

### Comparison
- [ ] `compare` returns both results and expected delta direction for a toy example.

### Explanations
- [ ] Every built-in scorer returns explanation string or structured reasons.

## Integration Tests
**How do we test component interactions?**

- [ ] Load real small context snippet from test fixtures; score with `method_id` selecting a section.

## End-to-End Tests
**What user flows need validation?**

- [ ] Optional: LLM-backed scorer with mocked client (no live API in CI).

## Test Data
**What data do we use for testing?**

- Minimal Markdown context with two `##` methods.
- Minimal dataset: 2–3 rows.

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Standard project test command when environment supports it.

## Manual Testing
**What requires human validation?**

- Readability of explanations for real prompts.

## Performance Testing
**How do we validate performance?**

- Optional benchmark on large dataset rows.

## Bug Tracking
**How do we manage issues?**

- Separate “metric definition” issues from implementation bugs.
