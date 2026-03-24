---
phase: planning
title: Planning — prompt-optimizer-agent
description: Milestones and tasks for the prompt optimizer agent and scorer integration
feature: prompt-optimizer-agent
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [x] **M1:** Requirements in repo; alignment with **context-engineering** (``prompt_methods_context.md`` shipped) and **`prompt-scorer`** / **stepwise-evaluation** when implemented.
- [ ] **M2:** Design approved (dialogue flow, tool contracts).
- [ ] **M3:** Agent MVP with mocked LLM + mocked scorer.
- [ ] **M4:** Integration with real context file + **`prompt-scorer`** when available.

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [ ] Task 1.1: Define session model (CO-STAR optional fields, prompt versions).
- [ ] Task 1.2: Stub **`prompt-scorer`** adapter (matches **`prompt-scorer`** feature spec when ready).

### Phase 2: Core Features
- [ ] Task 2.1: Implement CO-STAR question flow (first question = task description / CO-STAR framing per requirements).
- [ ] Task 2.2: Load context-engineered input; proposal generation with method citation + mixing.
- [ ] Task 2.3: Apply accepted proposal to user prompt using method rules.
- [ ] Task 2.4: Invoke scorer **before** and **after** modification at defined points.

### Phase 3: Integration & Polish
- [ ] Task 3.1: CLI or chat entrypoint documentation.
- [ ] Task 3.2: Error handling for missing context or scorer failures.

## Dependencies
**What needs to happen in what order?**

- **context-engineering** produces ``sources/data/context/prompt_methods_context.md`` (**implemented**).
- **`prompt-scorer`** (+ **stepwise-evaluation** / Braintrust) defines tool signature; agent blocked until scorer MVP exists.

## Timeline & Estimates
**When will things be done?**

- Dialogue + apply loop is medium effort; mixing logic may need prompt iteration.

## Risks & Mitigation
**What could go wrong?**

- **Over-mixing** methods confuses users → limit N methods per proposal; show labels.
- **Scorer drift** if pre/post definitions unclear → document call sites in implementation guide.

## Resources Needed
**What do we need to succeed?**

- Sample context file from **context-engineering**; **`prompt-scorer`** mock for tests.
