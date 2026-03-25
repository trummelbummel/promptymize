from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from auto_prompt.promptymization.context_generation import PromptMethodsContext
from auto_prompt.promptymization.dspy_lm import create_dspy_lm_from_env


def _ollama_tags(api_base: str) -> list[str]:
    tags_url = api_base.rstrip("/") + "/api/tags"
    with urllib.request.urlopen(tags_url, timeout=5) as resp:  # noqa: S310
        data = json.loads(resp.read().decode("utf-8"))
    models = data.get("models") or []
    return [m.get("name", "") for m in models]


def test_context_engineering_integration_uses_real_llm(tmp_path: Path) -> None:
    """
    Integration test using the real DSPy LM + real scraped markdown input.

    Opt-in:
    - set `AUTO_PROMPT_RUN_REAL_INTEGRATION=1` (recommended before running locally).

    When enabled, the test assumes inputs are available:
    - if Ollama isn't reachable, the model isn't present, or `sources/data/**/page.md` is missing,
      it raises (does not skip).
    """

    if os.environ.get("AUTO_PROMPT_RUN_REAL_INTEGRATION", "").strip().lower() not in {"1", "true", "yes"}:
        pytest.skip("Enable AUTO_PROMPT_RUN_REAL_INTEGRATION=1 to run the real LLM integration test.")

    lm = create_dspy_lm_from_env()
    api_base = str(lm.kwargs.get("api_base", "")).strip()
    if not api_base:
        raise RuntimeError("DSPy LM api_base is missing; cannot verify Ollama availability.")

    model = os.environ.get("DSPY_MODEL", "gemma3:4b").strip()

    try:
        available_models = _ollama_tags(api_base)
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama not reachable at {api_base!r}: {exc}") from exc

    if model not in available_models:
        raise RuntimeError(f"Ollama model {model!r} not available; got {available_models}")

    repo_root = Path(__file__).resolve().parents[2]
    pages = sorted(repo_root.glob("sources/data/**/page.md"))
    if not pages:
        raise FileNotFoundError("No real scraper page.md inputs found under sources/data.")

    # Keep input bounded so the test is fast enough for local runs.
    excerpt = pages[0].read_text(encoding="utf-8")[:6000].strip()
    if not excerpt:
        raise ValueError("Selected sources/data/**/page.md excerpt is empty.")

    data_root = tmp_path / "sources" / "data"
    (data_root / "batch1").mkdir(parents=True)
    (data_root / "batch1" / "source.md").write_text(excerpt, encoding="utf-8")

    pipeline = PromptMethodsContext(data_root=data_root)
    out_path = pipeline.build_context()
    out_text = out_path.read_text(encoding="utf-8")

    assert out_text.strip(), "Expected non-empty context output from real LM."
    assert re.search(r"^##\s+\S+", out_text, flags=re.M), "Expected at least one '## <method>' header."

    # Orchestrator moves processed source folders.
    assert not (data_root / "batch1" / "source.md").exists()
    assert (data_root / "processed" / "batch1" / "source.md").exists()

