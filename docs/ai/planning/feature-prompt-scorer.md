---
phase: planning
title: Planning — prompt-scorer
description: Milestones for scorer core, extension API, dataset modes, and agent integration
feature: prompt-scorer
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [ ] **M1:** Requirements + output schema agreed (`/review-requirements`).
- [ ] **M2:** Design: `ScoreResult`, registry, context vs dataset (`/review-design`).
- [ ] **M3:** Core implementation + unit tests.
- [ ] **M4:** Integration with **`prompt-optimizer-agent`** (tool adapter).

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [ ] Task 1.1: Define `ScoreResult`, `ComparisonResult`, and exception types.
- [ ] Task 1.2: Implement `ScorerRegistry` + base class / protocol.

### Phase 2: Core Features
- [ ] Task 2.1: Built-in **context-only** scorer using context-engineering Markdown (e.g. checklist against selected method section).
- [ ] Task 2.2: Built-in **dataset** scorer skeleton (minimal dataset format).
- [ ] Task 2.3: `compare()` implementation with deltas.
- [ ] Task 2.4: Explanation field populated for all built-ins.

### Phase 3: Integration & Polish
- [ ] Task 3.1: Document extension guide (register custom scorer).
- [ ] Task 3.2: Thin adapter for **`prompt-optimizer-agent`** (import path, kwargs).

## Dependencies
**What needs to happen in what order?**

- Stable **context file** format from **context-engineering** helps context-only scorers.
- **`prompt-optimizer-agent`** depends on this API; ship scorer API before final agent wiring.

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
