---
phase: implementation
title: Implementation — user-interface
description: Implementation notes for the primary UI shell and backend integration
feature: user-interface
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Document Node/Python version and package manager per chosen stack.
- Run backend locally; point UI `API_BASE_URL` at dev server.
- Configure **Google OAuth** client ID/secret for the REST API and frontend redirect URIs.

## Code Structure
**How is the code organized?**

- Separate `frontend/` (or `ui/`) from `src/auto_prompt` unless using embedded Python UI (TBD).
- Shared types: optional `openapi.json` or TypeScript types generated from backend.

## Implementation Notes
**Key technical details to remember:**

### Core Features
- **Primary:** route `/` or `/app` lands in **agent** flow, not settings.
- **REST:** all agent and scorer interactions use **REST** JSON endpoints (no WebSocket dependency).
- **Auth:** protect API routes; only **Google-authenticated** sessions (or valid tokens) may call agent/scorer.
- **Context:** server loads ``sources/data/context/prompt_methods_context.csv`` for agent and scorer (same as design), and may load per-method files from ``sources/data/context/methods/`` for direct method-apply actions.
- **Braintrust:** scoring endpoints call **prompt-scorer** only; scorer uses **stepwise-evaluation** (env from **`.env.example`**).
- **Compare:** bind “Accept new” / “Keep old” to API calls that update session state.
- **Scores:** render **before** and **after** ``ScoreResult`` values and **deltas** from ``ComparisonResult``; render `explanation` per score; never truncate without “show more.”
- **Upload:** client-side size check + server validation; show parse errors.

### Patterns & Best Practices
- Single source of truth for “current prompt” in client store after server confirms.

## Integration Points
**How do pieces connect?**

- **`prompt-optimizer-agent`** for dialogue and proposals.
- **`prompt-scorer`** for scores; same payload as non-UI clients.

## Error Handling
**How do we handle failures?**

- Scorer failure: show error banner + retry; preserve last good scores if any.

## Performance Considerations
**How do we keep it fast?**

- Debounce re-score if user edits rapidly; optional “Evaluate” button vs auto.

## Security Notes
**What security measures are in place?**

- Validate uploads; sanitize filenames; no execution of uploaded content as code.
