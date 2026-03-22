---
phase: testing
title: Testing — prompt-method-scraper
description: Test strategy for config-driven scraping and Markdown output
feature: prompt-method-scraper
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- Unit tests for config parsing, path building, and handler selection (mocked HTTP).
- Integration tests with recorded fixtures or mocks for HTML/PDF boundaries.
- Align tests with `tests/` mirroring `src/` layout.

## Unit Tests
**What individual components need testing?**

### Config / paths
- [ ] Valid YAML produces expected list of `(folder_name, url)` pairs.
- [ ] Invalid YAML or missing fields raises or reports clearly.

### Fetch / conversion (mocked)
- [ ] HTML fixture → expected Markdown fragment or writer calls.
- [ ] arXiv URL classification → correct handler invoked.
- [ ] PDF fixture → extracted text non-empty or explicit fallback path.

## Integration Tests
**How do we test component interactions?**

- [ ] End-to-end with temporary `resources/data` dir: one synthetic target, assert file created.
- [ ] Failure path: HTTP error logged and run completes or exits per policy.

## End-to-End Tests
**What user flows need validation?**

- [ ] “Run scraper from config” produces files under expected folders (staging/manual or CI with network disabled + mocks).

## Test Data
**What data do we use for testing?**

- Small HTML snippets; tiny PDF fixture; avoid checking in large binaries if possible.

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- `make test` / project standard once environment can reach PyPI/build deps.

## Manual Testing
**What requires human validation?**

- Spot-check a few live URLs from `scraper_targets.yaml` after implementation.
- Verify Markdown readability for arXiv PDFs.

## Performance Testing
**How do we validate performance?**

- Optional: time full run; not required for v1.

## Bug Tracking
**How do we manage issues?**

- Track failed URLs and site-specific breakages as regular issues.
