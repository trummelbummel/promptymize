---
phase: testing
title: Testing — prompt-optimizer-agent
description: Test strategy for elicitation, proposals, apply, and pre/post scoring
feature: prompt-optimizer-agent
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- **100% of orchestration logic** that does not depend on nondeterministic LLM output (state transitions, optional CO-STAR aggregation, apply stub, scorer call order).
- Mock DSPy/LLM and **`prompt-scorer`** in unit tests.

## Unit Tests
**What individual components need testing?**

### Session / CO-STAR
- [ ] All fields optional; empty session valid.
- [ ] Serialization or snapshot of state if persisted (if applicable).

### Proposal / apply (mocked LM)
- [ ] Given fixed LM outputs, proposal text and cited methods parsed correctly.
- [ ] `apply_proposal` produces expected string for controlled inputs.

### Scorer integration
- [ ] **Before** modification: scorer called with initial prompt when flow dictates.
- [ ] **After** modification: scorer called with new prompt after accept.
- [ ] Scorer exceptions handled per policy.

## Integration Tests
**How do we test component interactions?**

- [ ] End-to-end with fake context file and mocked LLM: user accepts proposal → prompt changes → two scorer invocations in order (exact order per spec).

## End-to-End Tests
**What user flows need validation?**

- [ ] Optional manual: real LM + real scorer in staging.

## Test Data
**What data do we use for testing?**

- Minimal context Markdown with two fake “methods”; tiny user prompts.

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Project standard test command when environment allows.

## Manual Testing
**What requires human validation?**

- Quality of proposals and creative mixing with real models.

## Performance Testing
**How do we validate performance?**

- Not critical for v1 unless batch usage.

## Bug Tracking
**How do we manage issues?**

- Track wrong method selection vs. scorer bugs separately.
