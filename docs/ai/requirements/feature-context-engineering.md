---
phase: requirements
title: Requirements — context-engineering
description: DSPy pipeline from scraped Markdown to deduplicated prompt-method context for agents
feature: context-engineering
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- Raw **scraper output** (`sources/data/**/*.md`) is verbose and repetitive. Agents that **modify prompts** need a **compact, structured context file** derived from that source text.
- Summaries must be **Markdown with clear structure**: each **header** corresponds to **one prompt method**; **bullet points** encode **actionable rules** for improving prompts.
- Users need **deduplication**: no repeated headers, no repeated bullets, and **semantically merged** content so the final context file contains **unique prompt-method material** only.

**Who is affected:** developers and automation that run summarization + downstream agents consuming the context file.

## Goals & Objectives
**What do we want to achieve?**

- **Primary goals**
  - Provide **DSPy modules** that ingest **source text** (from scraper `.md` files) and produce **structured Markdown** suitable for agent consumption, using ``PromptMethodSummarizer`` (and related signatures) for per-source summarization.
  - Enforce structure: **one summary block per prompt method** (header naming convention TBD in design), with **bullets as applicable rules**.
  - **Deduplicate** across inputs so the **aggregated context file** has **unique headers and unique bullets** at the level of “same prompt method / same rule.”
- **Secondary goals**
  - Composable pipeline (summarize → merge/dedupe → write artifact) aligned with existing `promptymization` code.
  - **Stepwise evaluation during context build:** when users **opt in** (CLI flag, env, or API parameter), the pipeline **invokes stepwise-evaluation** so **`context_engineering`** Braintrust evals can **log or run** against the **inputs and merged output** of that build—**without** going through **prompt-scorer**. Default behavior remains **no** Braintrust (plain merge).
  - Traceability optional later (which source file contributed which method)—non-goal for v1 unless requested.
- **Non-goals (initial)**
  - Perfect semantic deduplication at corpus scale without LLM calls (heuristics + LM-assisted dedupe as per design).
  - Real-time streaming updates; batch/offline generation is sufficient.

## User Stories & Use Cases
**How will users interact with the solution?**

- As a **user**, I want to **summarize source text into structured Markdown** with **headers that each represent one prompt method** and **bullet points that describe the method as rules** so an agent can **apply them to improve a prompt**.
- As a **user**, I want **no duplication in headers or bullet points** in the final output.
- As a **user**, I want **deduplicated summaries** so the **context file** contains **only unique content** related to each **prompt method** (no near-duplicate sections).
- As an **AI engineer**, I want **stepwise-evaluation** to run **during or right after** a **context-engineering** build so I can **regression-test summarization and merge quality** in **Braintrust** the same way as other pipeline steps.

**Workflows**

- Point pipeline at `sources/data` (scraped **`.md` only**), run generation, and **merge new summaries into the latest** canonical file ``sources/data/context/prompt_methods_context.md`` (dedupe after merge).
- **Optional:** enable **eval mode** on the same command so **stepwise-evaluation** records or executes **`context_engineering`** evals (requires Braintrust env; see **stepwise-evaluation** requirements).
- Re-runs **append/merge** into that file; prior unique content is preserved subject to dedupe rules (exact + optional LM-assisted).

**Edge cases**

- Two sources describe the **same** method with different wording → should collapse to **one header** and **merged unique bullets**.
- Empty or tiny inputs; non-Markdown noise; very long pages.
- Conflicting rules for the same method → design must specify (keep both, merge, or prefer newer).

## Success Criteria
**How will we know when we're done?**

- DSPy-based pipeline produces **structured Markdown** meeting the header/bullet semantics above.
- A **deduplication step** removes **duplicate headers** and **duplicate bullets** according to measurable rules (exact match minimum; semantic match as specified).
- **Acceptance:** documented **example** input(s) → output context with **no duplicate headers** and **no duplicate bullets** in the acceptance fixture.
- **Tests:** unit tests for pure helpers; mocked LLM tests for module wiring; core logic covered per project test rules.

## Constraints & Assumptions
**What limitations do we need to work within?**

- **Technical:** Use **DSPy** for LLM-related modules (`pyproject.toml` version); Python codebase patterns (OO, docstrings).
- **Assumptions:** Scraper output is available as `.md` under `sources/data`; LLM API/config available at runtime for summarization/dedupe signatures. **Eval mode** additionally assumes **Braintrust** credentials per **`.env.example`** (same as **stepwise-evaluation**).

## Questions & Open Items
**What do we still need to clarify?**

- [ ] **Header taxonomy:** fixed levels (`##` only) vs free-form; normalization of method names.
- [ ] **Dedupe strategy:** exact string only vs embedding/LM “same method” clustering.
- [x] **Output location:** canonical **merge-latest** file ``sources/data/context/prompt_methods_context.md`` under data root ``sources/data``. **prompt-optimizer-agent** and **prompt-scorer** load this path when improving or evaluating prompts.
- [x] **Incremental updates:** **merge into latest** — each pipeline run incorporates new material into ``prompt_methods_context.md`` with deduplication (no requirement for monotonic versioned filenames).
- [ ] **Ordering** of methods in the final context file (alphabetical, source order, confidence).
