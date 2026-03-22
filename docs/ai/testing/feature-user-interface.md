---
phase: testing
title: Testing — user-interface
description: Testing strategy for UI flows, comparison, scoring display, and uploads
feature: user-interface
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- **Component tests** for compare, score cards, upload validation.
- **E2E tests** for: open app → see proposal → choose old/new → see scores (mocked API if needed).
- **Accessibility:** keyboard focus on primary actions.

## Unit Tests
**What individual components need testing?**

### Compare / selection
- [ ] Selecting “new” vs “old” invokes correct callback with expected prompt ids/text.

### Score display
- [ ] Renders score fields and explanation when present; handles missing explanation gracefully.

### Upload
- [ ] Rejects oversize or wrong type; accepts valid fixture.

## Integration Tests
**How do we test component interactions?**

- [ ] With mocked backend: full flow from upload to displayed scores.

## End-to-End Tests
**What user flows need validation?**

- [ ] Happy path against staging backend (optional CI job).

## Test Data
**What data do we use for testing?**

- Short and long prompt strings; sample CSV for dataset upload.

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Frontend coverage tool per stack (TBD).

## Manual Testing
**What requires human validation?**

- Readability of explanations on small screens; color contrast.

## Performance Testing
**How do we validate performance?**

- Large prompt paste does not freeze main thread (debounce/virtualization if needed).

## Bug Tracking
**How do we manage issues?**

- Tag UI vs backend when scoring display mismatches API.
