---
phase: requirements
title: Requirements — prompt-optimizer-agent
description: Conversational agent for CO-STAR elicitation, context-grounded prompt improvement, and scoring hooks
feature: prompt-optimizer-agent
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- Users need help **iteratively improving prompts** using **structured elicitation** (CO-STAR) and **evidence-based suggestions** drawn from **context-engineered** material (summaries of scraped prompt methods).
- A **prompt-optimizer agent** should **ask questions**, **propose improvements** grounded in that context, optionally **apply** agreed changes, and **score** the prompt **before and after** modification—using a **separate prompt-scorer** capability (see feature **`prompt-scorer`**).

**Who is affected:** end users improving prompts; integrators wiring the agent to context files and the scorer tool.

- **Context file dependency:** the agent **must load** the merged latest context artifact at ``sources/data/context/prompt_methods_context.csv`` (output of **context-engineering**) to retrieve prompt methods. The CSV includes ``model_type`` labels and may contain multiple rows per method when a method applies to multiple model families.

## Goals & Objectives
**What do we want to achieve?**

- **Primary goals**
  - **Conversational flow:** The agent **asks the user questions**; the **first** question collects the **task description** framed by the **CO-STAR** dimensions:
    - **C**ontext — background to ground the model.
    - **O**bjective — what the model must accomplish.
    - **S**tyle — how information should be presented.
    - **T**one — emotional quality of the response.
    - **A**udience — who will read or use the output.
    - **R**esponse — desired output format (e.g. paragraphs, JSON, CSV).
  - **Context-grounded proposals:** After CO-STAR (or sufficient partial input), the agent **proposes prompt improvements** using the **context-engineered** file(s) that summarize **prompt methods** from scraped sources—selecting **best-fitting** methods and **creatively combining** multiple methods where helpful.
  - **Apply on acceptance:** If the user **accepts** a proposal, the agent **rewrites the prompt** by **applying the rules** of the **specific method(s)** referenced in that proposal.
  - **Scoring lifecycle:** Score the user’s prompt **before** any modification and **after** modification, via the **`prompt-scorer`** tool (defined elsewhere; this agent **calls** it, it does not redefine scoring logic here).
- **Secondary goals**
  - Clear UX copy and state (what was asked, what was proposed, what was applied).
  - Traceability: which context methods informed which proposal (high level).
  - CO-STAR enrichment should run in a **single prompt call** that jointly extends all six dimensions while considering all user-provided objectives.
  - Keep the **user in the loop**: before applying enriched details to the working prompt, the UI must ask the user to confirm whether the additions are improvements or should be edited.
- **Non-goals (this feature)**
  - Defining the **scoring rubric or implementation** (owned by **`prompt-scorer`**).
  - Replacing **context-engineering** pipeline (consumes its output).

## User Stories & Use Cases
**How will users interact with the solution?**

- As a **user**, I want to **specify answers to all CO-STAR-related questions**, but **every answer is optional**, so I can skip what I do not know yet.
- As a **user**, I want **proposals** for how to improve my prompt **from the context-engineered** material, using the **best-fitting** prompt **method(s)** for my situation.
- As a **user**, I want proposals that **creatively mix** multiple prompt methods to help me build a **better** prompt.
- As a **user**, if I **say yes** to a proposal, I want the agent to **modify my prompt** by **applying the rules** from the **specific method(s)** in that proposal.
- As a **user**, I want the agent to **score my prompt before** it is modified and **after** it has been modified (via **`prompt-scorer`**).
- As a **user**, I want the agent to generate one **joint CO-STAR extension draft** (all dimensions together, objective-aware), then let me review/approve/edit it in the UI before it is applied.

**Workflows (high level)**

1. User provides initial prompt (optional) and/or starts session.
2. Agent asks CO-STAR-oriented questions; user may answer partially.
3. Agent loads or receives **context-engineered** summary (path or injected text per integration).
4. Agent proposes improvement(s); user accepts/rejects or iterates.
5. On accept: agent applies changes; then scores **after**; **before**-scores occur when appropriate (e.g. at start or before apply—see open items).
6. Scoring always goes through **`prompt-scorer`** tool contract.

**Edge cases**

- Empty or missing context file; empty user prompt.
- User accepts only part of a multi-method proposal (clarify in design).
- Conflicting CO-STAR answers vs. existing prompt (agent should still behave safely).

## Success Criteria
**How will we know when we're done?**

- Agent implements **CO-STAR elicitation** with **optional** fields for all dimensions.
- Proposals are **grounded** in context-engineered content (no fabricated “methods” not present in context unless explicitly allowed as generic tips—TBD).
- **Accept** path produces an **updated prompt** aligned with cited method rules.
- **Two scoring calls** are supported: **pre-modification** and **post-modification**, delegating to **`prompt-scorer`**.
- Automated tests for **state machine / tool invocation** where LLM is mocked.

## Constraints & Assumptions
**What limitations do we need to work within?**

- **Technical:** DSPy or project-standard agent patterns; integrates with **`prompt-scorer`** API as specified in that feature.
- **Assumptions:** Context file format and location are stable (from **context-engineering**); user can supply a draft prompt string.

## Questions & Open Items
**What do we still need to clarify?**

- [ ] Exact **order** of questions after the first “task description” CO-STAR question (one mega-question vs. six separate questions).
- [ ] **When** “score before” runs: session start only, or also immediately before apply?
- [ ] **Partial acceptance** of multi-method proposals.
- [ ] How **creative mixing** is constrained (max methods, citation format in UI).
- [ ] Dependency: minimum viable **`prompt-scorer`** interface (tool name, inputs/outputs) for integration.
