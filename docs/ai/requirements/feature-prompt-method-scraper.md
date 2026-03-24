---
phase: requirements
title: Requirements — prompt-method-scraper
description: Scrape configured URLs (blogs, arXiv, PDFs) and store normalized Markdown under sources/data
feature: prompt-method-scraper
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- Users building or tuning prompts need **curated, local copies** of prompt-engineering guidance from the web (blogs, documentation, arXiv papers, PDFs) in a **consistent, machine-readable form** (Markdown) under version-controlled or inspectable storage.
- Today, sources are listed in `scraper_targets.yaml` (URLs grouped by `folder_name`), but the product needs a **clear, repeatable pipeline**: fetch remote content, normalize to Markdown, and persist under `sources/data` for downstream processing (e.g. summarization, context generation).
- **Who is affected:** developers and automation that consume `sources/data`; anyone maintaining the scraper config.

## Goals & Objectives
**What do we want to achieve?**

- **Primary goals**
  - **Deliver a full implementation** in the codebase (Python modules under ``auto_prompt.scraper``, wired to ``scraper_targets.yaml``)—not documentation-only. The scraper pipeline must be **executable** (CLI or Makefile entrypoint) and produce real artifacts on disk.
  - Support **config-driven** scraping: URLs and **associated folder names** for storage (as in `scraper_targets.yaml`).
  - Persist **only Markdown files** (``.md``) under `sources/data`—HTML, PDF, and other sources are **normalized to Markdown**; **no** required sidecar formats (e.g. no mandatory `meta.json`); optional debug artifacts are out of scope unless explicitly added later.
  - Support **blog/HTML pages** and **arXiv**-style sources, including **PDF** where applicable, with predictable on-disk layout.
- **Secondary goals**
  - Idempotent or safe re-runs (avoid corrupting data; clear behavior on duplicate runs—TBD in design).
  - Logging and errors that make failed URLs easy to fix.
- **Non-goals (initial)**
  - Full-text search UI or a public API for scraped data.
  - Scraping behind auth or paywalls without explicit support.
  - Guaranteeing completeness of every PDF extraction edge case (complex layouts may degrade gracefully).

## User Stories & Use Cases
**How will users interact with the solution?**

- As a **user**, I want to **download relevant files from the internet** and **store the content in Markdown format** so that I can process them offline and in pipelines.
- As a **user**, I want to **give URLs and associated folder names for storage in configuration** (`scraper_targets.yaml` or successor) so that I can organize sources by topic or provider without code changes.
- **Workflows**
  - Edit YAML: add `folder_name` + list of `url` entries.
  - Run scraper (CLI or documented entrypoint): **only** **`.md`** files land under `sources/data/<folder_name>/...` (one canonical Markdown artifact per scrape target per design).
- **Edge cases**
  - Redirects, rate limits, transient network failures.
  - arXiv abstract page vs PDF; duplicate URLs; very large PDFs.
  - Non-HTML content types and encoding issues.

## Success Criteria
**How will we know when we're done?**

- Config entries in `scraper_targets.yaml` (or documented schema) drive **where** and **what** is fetched.
- For each configured target, **Markdown output** exists under `sources/data` in the expected folder structure (exact file naming defined in design).
- arXiv and blog-style URLs are handled per agreed rules; PDFs yield extractable text reflected in Markdown or clearly documented fallback.
- Acceptance criteria are testable: at least **unit tests** for config parsing and path resolution, and **integration/smoke** tests where network is mocked.

## Constraints & Assumptions
**What limitations do we need to work within?**

- **Technical:** Existing project stack (Python, current scraper modules); respect `pyproject.toml` tool versions.
- **Legal/ethical:** Users must comply with site terms, robots.txt where applicable, and arXiv usage norms.
- **Assumptions:** `sources/data` is writable at runtime; outbound HTTPS available in deployment environments that run the scraper.

## Questions & Open Items
**What do we still need to clarify?**

- [x] **On-disk artifact:** **only** **`.md`** files; default single Markdown file per URL/target (e.g. ``page.md``—finalize in design) unless multiple URLs explicitly require multiple files.
- [ ] **Re-run behavior:** skip if unchanged, overwrite, or versioned subfolders?
- [ ] **PDF pipeline:** library choice and minimum quality bar for extracted text.
- [ ] **arXiv:** prefer abstract HTML, PDF, or both; handling of ancillary files.
- [ ] **ResearchGate** and similar: often restricted or JS-heavy—explicit support or exclude list?
