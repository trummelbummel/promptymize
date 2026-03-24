---
phase: requirements
title: Requirements — stepwise-evaluation
description: Braintrust-based evaluations per pipeline step, component, and end-to-end system output
feature: stepwise-evaluation
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- **AI engineers** and **prompt engineers** need **repeatable quality measurement** not only on **final system output** but on **each meaningful step** of their stack (e.g. context engineering, summarization, scraper output, agent turns). Ad-hoc “eyeballing” does not scale and cannot be compared across versions.
- Observations and qualitative judgments should translate into **named evaluations** (datasets, scorers, or Braintrust experiments) that run **consistently** and integrate with a **known eval platform**—here **Braintrust**.
- **Who is affected:** engineers maintaining this repo’s pipelines (scraper → context → agent → UI) and anyone tuning prompts or pipeline steps.

## Goals & Objectives
**What do we want to achieve?**

- **Primary goals**
  - **Braintrust is required** for this feature in production: the default and supported integration is the **Braintrust** SDK/API (no alternate “eval cloud” in scope). **Configuration** must document all **environment variables** (see **`.env.example`** in the repo root); apps load secrets from env, never from committed files.
  - Support **stepwise evaluation**: define and run **Braintrust** evals for **individual steps** (e.g. **context-engineering** output, summarization, **scraper** Markdown, **agent** turns) and for **end-to-end** traces. Stepwise evaluation is **general-purpose**—not limited to final prompt scoring.
  - **context-engineering integration:** the **context build** (`PromptMethodsContext` / `auto-prompt-build-context`) **must** be able to call **stepwise-evaluation** when eval mode is enabled, so **`context_engineering`** runs are **first-class during the CE phase** (not only via manual scripts or **prompt-scorer**).
  - Allow users to **create evaluations from their observations** (labels, examples, notes) and persist them in a form **Braintrust** consumes.
  - **prompt-scorer** **depends on** stepwise-evaluation for Braintrust-backed runs; stepwise-evaluation does **not** duplicate prompt-scorer’s user-facing API—see **prompt-scorer** requirements.
- **Secondary goals**
  - Map logical **pipeline steps** to **eval boundaries** (clear inputs/outputs per step).
- **Non-goals (initial)**
  - Replacing Braintrust with an in-house eval platform.
  - **Committed SLA** or latency guarantees for eval runs or Braintrust API availability.
  - Full production observability (APM); focus is **eval** workflows.

## User Stories & Use Cases
**How will users interact with the solution?**

- As an **AI engineer / prompt engineer**, I want to **define Braintrust-based evals** for **each prompt**, **each application component or step**, and **overall system output** so I can **track regressions and improvements** over time.
- As a **user**, I want to **create evaluations based on my observations** (curated examples, labels, notes) so they reflect **real failure modes** I care about.
- As a **user**, I want to **create evaluations for each step**—for example the **context-engineering step**—so I can **isolate** whether quality issues come from **upstream data**, **summarization**, or **downstream** usage.
- As a **user**, I want to **use Braintrust** for these evaluations so I get **centralized runs, comparisons, and (where supported) human/LLM scoring** in one place.

**Workflows**

- Define a **step key** (e.g. `context_engineering`, `scraper_markdown`, `agent_turn`, `end_to_end`).
- Register **inputs/outputs** for that step (or derive from existing modules).
- **From context-engineering:** when eval mode is on, the build passes **CE inputs/outputs** (e.g. merged context snippet, source list) into **stepwise-evaluation** for ``step_id=context_engineering``.
- Push **rows** (examples + optional labels) to Braintrust datasets or runs; attach **scorers** / eval functions per Braintrust patterns.
- Run eval **locally or in CI** (policy TBD) with API keys configured.

**Edge cases**

- Missing **Braintrust** credentials in deployment (must be treated as **misconfiguration** for any flow that runs evals; local **tests** may mock the client).
- Steps that call **external LLMs** (non-determinism)—evals should allow **thresholds** or **repeated sampling** policy (TBD).
- Large traces—**sampling** or **truncation** policy for logging.

## Success Criteria
**How will we know when we're done?**

- At least **one** documented **step-level** Braintrust eval (e.g. context-engineering) and a path for **system-level** eval is **implementable** from the repo.
- Users can **add** eval cases from **observations** (documented format: JSONL, UI export, or Braintrust UI—documented in design).
- **Braintrust** is **required** for product eval workflows; **`.env.example`** lists required env vars; integration code is **versioned** in the repo.
- **Acceptance:** a short **How to run step evals** section in implementation docs and a **smoke** test or dry-run where network is mocked/skipped.

## Constraints & Assumptions
**What limitations do we need to work within?**

- **Technical:** Python codebase; respect `pyproject.toml`; Braintrust SDK/API as of integration date.
- **Assumptions:** Users provision a **Braintrust** project and API key; all **Braintrust-related** env vars are **documented in `.env.example`** and set via deployment config or local `.env` (gitignored).
- **Legal:** Logged data may contain sensitive prompts—document **redaction** / **PII** guidance (TBD).

## Questions & Open Items
**What do we still need to clarify?**

- [ ] Exact **Braintrust** primitives (Experiments, Datasets, `Eval`, custom scorers) vs minimal REST usage—**default remains Braintrust SDK** as productized.
- [ ] **CI** policy: eval on every PR vs nightly vs manual.
- [x] **prompt-scorer** uses **stepwise-evaluation**; stepwise-evaluation is the **general** eval layer for any step or E2E trace.
- [ ] **Identifier** scheme for steps (`enum`, string registry) shared across docs and code.
