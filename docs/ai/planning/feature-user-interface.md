---
phase: planning
title: Planning — user-interface
description: Milestones for UI shell, agent integration, scoring views, and upload
feature: user-interface
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [ ] **M1:** Requirements + information architecture (`/review-requirements`).
- [ ] **M2:** Design: wireframes + API contract with backend (`/review-design`).
- [ ] **M3:** MVP UI: chat + compare + score display (mocked backend).
- [ ] **M4:** Live integration with **agent** + **prompt-scorer** + upload.

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [ ] Task 1.1: Choose stack and app location in repo (e.g. `frontend/` or `ui/`).
- [ ] Task 1.2: Define OpenAPI or shared types for session, scores, uploads.

### Phase 2: Core Features
- [ ] Task 2.1: Agent conversation view (primary entry).
- [ ] Task 2.2: Compare view: two prompts + select old vs new.
- [ ] Task 2.3: Score + explanation panel per version (bind to `ScoreResult`).
- [ ] Task 2.4: Dataset upload flow and validation.

### Phase 3: Integration & Polish
- [ ] Task 3.1: Error handling, empty states, accessibility pass.
- [ ] Task 3.2: E2E tests for happy path (optional).

## Dependencies
**What needs to happen in what order?**

- **`prompt-scorer`** API stable for score/explanation binding.
- **`prompt-optimizer-agent`** exposes stable turn + proposal contract.

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
