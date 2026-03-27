---
phase: requirements
title: Requirements — prompt-scorer
description: Extensible prompt scoring with optional dataset, method selection, and explanations
feature: prompt-scorer
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- Users need **repeatable, explainable** evaluation of **prompt quality**—not only subjective judgment. The **prompt scorer** exposes **score** / **compare** APIs and **must depend on stepwise-evaluation (Braintrust)** for running evals and recording results—**it does not reimplement** Braintrust clients, experiment wiring, or duplicate Braintrust-native scoring flows.
- **stepwise-evaluation** is the **general** layer: it supports evals for **prompts**, **intermediate pipeline steps** (e.g. context-engineering output), and **end-to-end** traces. **prompt-scorer** is a **caller/adapter** that uses stepwise-evaluation for prompt-focused evals (including **compare**) while reusing the same Braintrust configuration. **context-engineering** may also call **stepwise-evaluation** **directly** during the **CE build** (``context_engineering`` step) when eval mode is on—**not** via **prompt-scorer**.
- The scorer remains **extensible** at the **policy** level (which eval profiles / step IDs to run, how to map prompts and context into Braintrust rows). It should accept **optional data** (a **dataset**) when provided, and must work **without** a dataset by using the **merged context file** at ``sources/data/context/prompt_methods_context.csv`` (from **context-engineering**) when no data is supplied. **Loading this context file is required** for scorer behavior that aligns with prompt methods in production (same file the **prompt-optimizer-agent** uses).
- **Compare:** ``compare(before, after)`` must expose **both** scores, **both** explanations, and **deltas** for the **user-interface** to render.
- **Who is affected:** users of **`prompt-optimizer-agent`** (which calls this tool) and any developer integrating scoring into workflows.

## Goals & Objectives
**What do we want to achieve?**

- **Primary goals**
  - Provide a **prompt-scorer** facade that **scores** and **compares** prompts by delegating eval execution to **stepwise-evaluation (Braintrust)** rather than reimplementing platform calls.
  - Support **objective measures** (numeric scores, rubric dimensions, pass/fail flags—exact shape in design; surfaced from Braintrust / wrapped scorers per design) as output.
  - Support **comparison** between a **previous prompt version** and an **improved** version (side-by-side scores and deltas).
  - Allow the user to **select a method for evaluation** (e.g. evaluate against a specific **prompt method** from the context file, or a named scoring strategy).
  - Support **dataset-based** scoring when a dataset is provided; support **context-only** scoring when **no dataset** is provided (context file suffices).
  - Return **explanations** for **why** the score is what it is (short rationale, factors, or structured reasons).
- **Secondary goals**
  - Clear API for **`prompt-optimizer-agent`** and other callers (single entry point for “score this prompt”).
  - Testability: pure scoring logic separable from LLM calls when needed.
- **Non-goals (initial)**
  - Defining a single “ground truth” for all domains; **quality** remains **pluggable** per eval configuration.
  - Guaranteeing statistical validity of every metric without documented assumptions.
  - **Latency / SLA** guarantees for eval runs (no committed SLA for scoring or Braintrust round-trips).

## User Stories & Use Cases
**How will users interact with the solution?**

- As a **user**, I want **objective measures** (or structured scores) of **my prompt quality** so I can track improvement.
- As a **user**, I want to **compare my previous prompt version and the improved prompt version** so I can see whether changes helped.
- As a **user**, I want to **select a method for evaluation** (e.g. a named prompt method or evaluation profile) so scoring aligns with what I care about.
- As a **user**, I want to **use a dataset for scoring** when I have labeled or example inputs.
- As a **user**, I want to **score the prompt without a dataset** when I only have the prompt and the **context file** of summarized methods.
- As a **user**, I want to **extend scoring** with **new scoring functions** where **I define quality** (register custom scorers).
- As a **user**, I want **explanations** for **why** the score is the way it is.

**Workflows**

- **Context-only:** `score(prompt, context=..., dataset=None)` → scores + explanations.
- **With dataset:** `score(prompt, dataset=..., context=...)` → same, possibly richer metrics.
- **Compare:** `compare(prompt_a, prompt_b, options...)` → per-metric comparison and delta.
- **Extend:** add **Braintrust** eval definitions or stepwise-evaluation **profiles**—do **not** add a second eval platform inside **prompt-scorer**.

**Edge cases**

- Empty prompt; empty context; dataset with missing fields.
- Conflicting selected method vs available context sections.

## Success Criteria
**How will we know when we're done?**

- API documented; **at least one** built-in scoring function and a **documented extension point** for new functions.
- **Two modes** work: **with** and **without** dataset (context-only path explicitly tested).
- **Comparison** API returns interpretable **before/after** or **A/B** style results.
- **Explanations** always returned (or explicit empty rationale with reason—TBD).
- Unit tests for registry, dispatch, and comparison logic; mocks for LLM if used.

## Constraints & Assumptions
**What limitations do we need to work within?**

- **Technical:** Python, project style (OO, Sphinx docstrings); **Braintrust** credentials and related settings via **environment variables** documented in **`.env.example`** (and loaded by config as applicable)—see **stepwise-evaluation** requirements.
- **Assumptions:** Context file at ``sources/data/context/prompt_methods_context.csv`` (merge-latest) is available when using context-only mode; dataset schema agreed per eval.

## Questions & Open Items
**What do we still need to clarify?**

- [ ] Exact **output schema** (single number vs multi-dimensional rubric) mapping from Braintrust responses.
- [ ] Whether “**select a method**” means **context section** (prompt method) vs **named Braintrust eval** profile.
- [ ] **Dataset format** (JSONL, CSV, in-memory list) and required columns per eval.
- [ ] **Objectivity:** which metrics are rule-based vs LLM-judged (and how to label them in explanations).
- [x] **Dependency:** **prompt-scorer** uses **stepwise-evaluation**; no duplicate Braintrust integration.
