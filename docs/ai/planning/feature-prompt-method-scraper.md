---
phase: planning
title: Planning — prompt-method-scraper
description: Tasks, dependencies, and risks for the prompt-method-scraper feature
feature: prompt-method-scraper
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [ ] **M1:** Requirements signed off (`/review-requirements`).
- [ ] **M2:** Design agreed (storage layout, arXiv/PDF behavior) (`/review-design`).
- [ ] **M3:** Implementation + tests merged.
- [ ] **M4:** Smoke run against real `scraper_targets.yaml` (optional, network-dependent).

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [ ] Task 1.1: Confirm YAML schema and document it next to `scraper_targets.yaml`.
- [ ] Task 1.2: Map `folder_name` → `resources/data/<folder_name>` and list existing scraper entrypoints.

### Phase 2: Core Features
- [ ] Task 2.1: Ensure blog/HTML URLs produce Markdown under configured folders.
- [ ] Task 2.2: arXiv URLs: define and implement abstract vs PDF strategy.
- [ ] Task 2.3: PDF download + text extraction → Markdown or documented companion format.

### Phase 3: Integration & Polish
- [ ] Task 3.1: CLI/Makefile target for “run full scrape from config.”
- [ ] Task 3.2: Logging, exit codes, and idempotency behavior documented.

## Dependencies
**What needs to happen in what order?**

- Design decisions (storage layout, re-run policy) before large refactors.
- Tests can use mocks for network/PDF to avoid flaky CI.

## Timeline & Estimates
**When will things be done?**

- TBD after design review; PDF handling often dominates effort.

## Risks & Mitigation
**What could go wrong?**

- **Site blocking / rate limits:** retries, backoff, document manual runs.
- **PDF quality:** fallback message in Markdown, optional “raw extract” file.
- **ResearchGate / heavy JS:** may exclude or mark as unsupported.

## Resources Needed
**What do we need to succeed?**

- Python deps already in `pyproject.toml`; add PDF library only if approved.
- Sample URLs from `scraper_targets.yaml` for manual verification.
