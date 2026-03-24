---
phase: testing
title: Testing — stepwise-evaluation
description: Tests for step registry, record shape, and mocked Braintrust
feature: stepwise-evaluation
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- **Unit:** step registry, record serialization, observation JSONL parsing.
- **Integration:** mocked Braintrust client receives expected payloads when **context-engineering** build runs with eval mode (**context_engineering** step), and for **prompt-scorer** paths.
- No live Braintrust calls in default CI.

## Unit Tests
**What individual components need testing?**

### Step registry
- [ ] Known `step_id` values resolve to metadata.
- [ ] Unknown step raises or returns explicit error.

### Observation import
- [ ] Valid JSONL produces list of `EvalRecord`-like dicts.
- [ ] Invalid lines skipped or fail with clear error per policy.

## Integration Tests
**How do we test component interactions?**

- [ ] Patch Braintrust SDK: assert `log` / dataset insert called with expected fields for a stub pipeline run.
- [ ] **Context build:** run orchestrator with eval flag + mock stepwise; assert **post-merge** hook order (merge committed before eval emit).

## End-to-End Tests
**What user flows need validation?**

- [ ] Optional manual: single eval run against real Braintrust project (non-CI).

## Test Data
**What data do we use for testing?**

- Tiny Markdown snippets for context-engineering step; minimal JSONL fixtures.

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Standard `make test` / `uv run pytest`.

## Manual Testing
**What requires human validation?**

- Braintrust UI shows expected columns and scores.

## Performance Testing
**How do we validate performance?**

- Optional: batch size limits only.

## Bug Tracking
**How do we manage issues?**

- Separate “Braintrust outage” from “wrong metric” bugs.
