# Rendered architecture diagrams

Sources are **`.mmd`** files (plain Mermaid). **`.svg`** files are generated for viewing in the repo or docs viewers.

| Diagram | Source | SVG |
|--------|--------|-----|
| End-to-end system | `00-system-end-to-end.mmd` | [00-system-end-to-end.svg](00-system-end-to-end.svg) |
| Context engineering | `01-context-engineering.mmd` | [01-context-engineering.svg](01-context-engineering.svg) |
| Prompt-method scraper | `02-prompt-method-scraper.mmd` | [02-prompt-method-scraper.svg](02-prompt-method-scraper.svg) |
| Stepwise evaluation | `03-stepwise-evaluation.mmd` | [03-stepwise-evaluation.svg](03-stepwise-evaluation.svg) |
| Prompt scorer | `04-prompt-scorer.mmd` | [04-prompt-scorer.svg](04-prompt-scorer.svg) |
| Prompt optimizer agent | `05-prompt-optimizer-agent.mmd` | [05-prompt-optimizer-agent.svg](05-prompt-optimizer-agent.svg) |
| User interface | `06-user-interface.mmd` | [06-user-interface.svg](06-user-interface.svg) |

**Regenerate** (from this directory):

```bash
for f in *.mmd; do base="${f%.mmd}"; curl -fsS -o "${base}.svg" -X POST "https://kroki.io/mermaid/svg" --data-binary "@$f"; done
```

Keep **`.mmd`** in sync with the `` ```mermaid `` `` blocks in `../README.md` and `../feature-*.md`.
