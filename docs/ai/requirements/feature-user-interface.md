---
phase: requirements
title: Requirements — user-interface
description: Primary UI for interacting with the prompt optimizer agent, comparison, scoring, and data upload
feature: user-interface
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- Users need a **primary, approachable surface** to work with the **prompt-optimizer agent** and related capabilities (**prompt-scorer**, optional datasets). Today, interaction without a UI is secondary; the **user interface** should be the **main option** for driving the workflow.
- Users must **compare prompts**, **inspect scores and explanations**, **choose between an old and a newly proposed prompt**, and **upload evaluation data** when available.

**Who is affected:** end users improving prompts; anyone who prefers GUI over CLI/API.

## Goals & Objectives
**What do we want to achieve?**

- **Primary goals**
  - Provide a **user interface** that is the **default / main** way to interact with the **agent** (not the only way, but the recommended path).
  - Support **prompt comparison** (e.g. side-by-side or before/after) with clear labeling.
  - Display **scores** for each prompt version shown **and** **explanations** for those scores (from **`prompt-scorer`**).
  - When the agent **proposes a new prompt version**, let the user **select the new proposal** or **keep the previous** prompt.
  - Allow **uploading data** (evaluation dataset) when the user has data for **prompt evaluation**; support flows where **no file** is uploaded (context-only scoring per **`prompt-scorer`**).
- **Secondary goals**
  - Accessible, readable layout for long prompts and explanations.
  - Clear session state: which prompt is “current,” which is “candidate.”
- **Non-goals (initial)**
  - Full mobile-native apps (unless web responsive is sufficient).
  - Replacing programmatic APIs for automation (CLI/API may remain for power users).

## User Stories & Use Cases
**How will users interact with the solution?**

- As a **user**, I want the **UI to be the main way** to interact with the **agent** so I can complete tasks without editing config files or scripts.
- As a **user**, I want to **compare a prompt** (e.g. previous vs proposed) so I can decide what to keep.
- As a **user**, I want to **see the scores of each prompt** and **explanations for the score** so I understand quality and trade-offs.
- As a **user**, when a **new version is proposed**, I want to **select the new prompt** or **select the old prompt** explicitly.
- As a **user**, I want to **upload data** if I have data for **evaluation** of the prompt.

**Workflows**

- Start session → (optional) paste or upload prompt → interact with agent → see proposal → **compare** → view **scores + explanations** for each side → **accept new** or **keep old**.
- Optional: attach **dataset** file before or during scoring; **skip** if not needed.

**Edge cases**

- Very long prompts; failed uploads; invalid file types; scorer errors with user-friendly messages.

## Success Criteria
**How will we know when we're done?**

- UI supports the flows above without requiring CLI for the same actions.
- **Comparison** view is unambiguous (labels, timestamps, or version ids).
- **Scores and explanations** surface **`prompt-scorer`** outputs faithfully (no silent drop of explanation text).
- **Upload** path documented (accepted formats, size limits—TBD in design).
- Smoke tests or E2E tests for critical paths (stack TBD in design).

## Constraints & Assumptions
**What limitations do we need to work within?**

- **Technical:** Web stack or existing project choice (TBD); must call backend/agent APIs securely.
- **Assumptions:** Backend exposes stable endpoints for agent turns, scoring, and file upload.

## Questions & Open Items
**What do we still need to clarify?**

- [ ] **Framework** (web app, desktop, embedded in IDE) and stack.
- [ ] **Authentication** (single-user local vs multi-user).
- [ ] **Dataset** formats and max size for upload.
- [ ] **Real-time** vs page-refresh interaction model.
- [ ] **Offline** use or online-only.
