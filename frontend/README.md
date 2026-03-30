# Frontend MVP Shell

This folder contains a minimal browser UI shell for the user-interface feature.

## What it covers

- Session creation (`POST /v1/sessions`)
- Agent message send (`POST /v1/sessions/{session_id}/messages`)
- Prompt-method dropdown load (`GET /v1/methods?session_id=...`)
- Selected method apply (`POST /v1/methods/{method_id}/apply`)
- Score prompt (`POST /v1/scoring/score`)
- Compare prompts (`POST /v1/scoring/compare`)

## Run

Serve this folder with any static file server and ensure your backend exposes the
REST routes at `http://localhost:8000` (or set `window.API_BASE_URL` before loading `main.js`).

Example:

```bash
python -m http.server 5173
```

Then open: `http://localhost:5173/frontend/`
