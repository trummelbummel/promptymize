---
phase: planning
title: Planning — user-interface
description: Milestones for UI shell, agent integration, scoring views, and upload
feature: user-interface
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [x] **M1:** Requirements + information architecture documented in repo; wire **prompt-scorer** (no Braintrust in browser—backend/scorer runs evals).
- [x] **M2:** Design: wireframes + API contract with backend (`/review-design`).
- [x] **M3:** MVP UI: chat + compare + score display (mocked backend).
- [ ] **M4:** Live integration with **agent** + **prompt-scorer** + upload.

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [x] Task 1.1: Choose stack and app location in repo (e.g. `frontend/` or `ui/`).
- [ ] Task 1.2: Define OpenAPI or shared types for session, scores, uploads, **Google OAuth**, and **REST** routes; include one route per executable UI step.
- [ ] Task 1.3: Implement **Google OAuth** on the web app and **REST** session/JWT handoff to the backend.

### Phase 2: Core Features
- [x] Task 2.1: Agent conversation view (primary entry).
- [x] Task 2.2: Compare view: two prompts + select old vs new.
- [x] Task 2.3: Score + explanation panel: bind to ``ScoreResult``; for **compare**, show **before**, **after**, **both explanations**, and **deltas** from ``ComparisonResult``.
- [x] Task 2.4: Dataset upload flow and validation.
- [x] Task 2.5: Backend loads ``sources/data/context/prompt_methods_context.csv`` for agent + scorer on session start, filtering by target ``model_type`` (and including ``all`` rows).
- [x] Task 2.6: Add **step execution routes** so each UI button triggers one specific backend step independently.
- [x] Task 2.7: Add **step rerun routes** that re-execute any prior step and return refreshed output for UI state updates.
- [x] Task 2.8: Add dedicated **scoring routes** for score/compare so users can execute scoring independently and view results in UI.
- [x] Task 2.9: Add **prompt-method dropdown** populated from context-engineering method outputs (method files/metadata).
- [x] Task 2.10: Wire dropdown selection to a dedicated step route that applies the selected method to the current prompt draft and returns transformed prompt text.

### Phase 3: Integration & Polish
- [ ] Task 3.1: Error handling, empty states, accessibility pass.
- [ ] Task 3.2: E2E tests for happy path (optional).

## Dependencies
**What needs to happen in what order?**

- **`prompt-scorer`** API stable (delegates to **stepwise-evaluation** / Braintrust for eval runs).
- **`prompt-optimizer-agent`** exposes stable turn + proposal contract.
- **Context path** ``prompt_methods_context.csv`` — matches **context-engineering** output (**implemented**, with model-labeled rows).
- **REST API** is the main entrypoint for UI-triggered execution; route-per-step contracts must be stable before frontend wiring.

## Timeline & Estimates
**When will things be done?**

- MVP depends on backend readiness; UI can mock early.

## Risks & Mitigation
**What could go wrong?**

- **Schema drift** between UI and scorer → shared types or codegen.
- **Large prompts** break layout → use scrollable panels and monospace option.

## Resources Needed
**What do we need to succeed?**

- Design tokens or minimal style guide; test dataset samples.
