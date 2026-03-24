---
phase: planning
title: Planning — prompt-scorer
description: Milestones for scorer core, extension API, dataset modes, and agent integration
feature: prompt-scorer
---

# Project Planning & Task Breakdown

**Implementation note:** **prompt-scorer** is a **facade** only—**Braintrust** calls live in **stepwise-evaluation**. Phase 2 work is “wire prompts/context/datasets into stepwise + map results,” not a separate scorer SDK.

## Milestones
**What are the major checkpoints?**

- [ ] **M1:** Requirements + output schema agreed (`/review-requirements`).
- [ ] **M2:** Design: `ScoreResult`, registry, context vs dataset (`/review-design`).
- [ ] **M3:** Core implementation + unit tests.
- [ ] **M4:** Integration with **`prompt-optimizer-agent`** (tool adapter).

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [ ] Task 1.1: Define `ScoreResult`, `ComparisonResult`, and exception types (stable for agent/UI).
- [ ] Task 1.2: Implement **eval profile registry** (name → stepwise-evaluation / Braintrust config)—**avoid** duplicating Braintrust client logic here.

### Phase 2: Core Features
- [ ] Task 2.1: **Context-only** path: default ``sources/data/context/prompt_methods_context.md``, invoke **stepwise-evaluation** for configured eval.
- [ ] Task 2.2: **Dataset** path: adapt rows → stepwise-evaluation batch / Braintrust dataset format.
- [ ] Task 2.3: `compare()` — two runs via stepwise, return **both** scores, explanations, **deltas** for UI.
- [ ] Task 2.4: Map Braintrust / stepwise outputs into **explanation** fields on `ScoreResult`.

### Phase 3: Integration & Polish
- [ ] Task 3.1: Document extension guide (new eval profiles in Braintrust / stepwise, not new Python “scorer classes” unless thin wrappers).
- [ ] Task 3.2: Thin adapter for **`prompt-optimizer-agent`** (import path, kwargs).

## Dependencies
**What needs to happen in what order?**

- **stepwise-evaluation** must ship **before** or **with** scorer MVP (scorer has no Braintrust without it).
- **context-engineering** outputs ``prompt_methods_context.md`` (**available**); agent/UI depend on scorer API once defined.

## Timeline & Estimates
**When will things be done?**

- Registry + one built-in is small; LLM-heavy scorers need prompt tuning.

## Risks & Mitigation
**What could go wrong?**

- **“Objective”** claims for LLM judges → label outputs as model-based in explanations.
- **Dataset leakage** or schema mismatch → validate dataset at API boundary.

## Resources Needed
**What do we need to succeed?**

- Example context file; tiny sample dataset for tests.
