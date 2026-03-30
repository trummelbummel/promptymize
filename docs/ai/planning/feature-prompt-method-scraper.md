---
phase: planning
title: Planning — prompt-method-scraper
description: Tasks, dependencies, and risks for the prompt-method-scraper feature
feature: prompt-method-scraper
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [x] **M1:** Requirements in repo (Markdown-only persistence, ``sources/data`` layout).
- [x] **M2:** Design agreed — output **``.md`` only**, nested under ``sources/data/<sanitized_folder_name>/``; merge-latest context is downstream (**context-engineering**).
- [ ] **M3:** Implementation + tests merged.
- [ ] **M4:** Smoke run against real `scraper_targets.yaml` (optional, network-dependent).

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [x] Task 1.1: YAML schema documented in a header comment atop ``scraper_targets.yaml`` (``folder_name``, ``url`` list).
- [x] Task 1.2: Map `folder_name` → output under data root — ``auto_prompt.scraper.paths.resolve_output_dir`` + ``sanitize_folder_name`` in ``src/``; default data root ``sources/data``. **Note:** ``tests/scraper/`` not present in repo yet—add when scraper package is restored.

### Phase 2: Core Features
- [x] Task 2.1: **Implement** blog/HTML URL handling → Markdown under configured folders (production code path in ``auto_prompt.scraper.web_scraper``; HTML→Markdown + JS-loading-shell guard).
- [ ] Task 2.2: arXiv URLs: define and implement abstract vs PDF strategy.
- [ ] Task 2.3: PDF download + text extraction → Markdown or documented companion format.

### Phase 3: Integration & Polish
- [x] Task 3.1: CLI/Makefile target for “run full scrape from config.” (``promptymize-web-scrape batch`` + ``make scrape-batch``).
- [x] Task 3.2: Logging + non-zero exit on failed URLs implemented (per-URL stderr lines; run fails if any URL fails).

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
- **Current reality check:** many configured URLs (notably Medium/ResearchGate) return ``403`` in real runs; treat as expected external-blocking risk and keep per-URL failure reporting explicit.

## Resources Needed
**What do we need to succeed?**

- Python deps already in `pyproject.toml`; add PDF library only if approved.
- Sample URLs from `scraper_targets.yaml` for manual verification.
