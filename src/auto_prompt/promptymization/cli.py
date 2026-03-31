from __future__ import annotations

import argparse
import os
from pathlib import Path

from auto_prompt.preprocessing.context_engineering import PromptMethodsContext


def main() -> None:
    """
    Command-line entry for promptymization (e.g. build context from scraped Markdown).

    :return: None; prints the written context file path.
    """

    parser = argparse.ArgumentParser(
        prog="auto-prompt-build-context",
        description="Merge scraped .md summaries into sources/data/context/prompt_methods_context.csv.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Root containing scraped Markdown (default: <project>/sources/data).",
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="After merge, log a context_engineering row to Braintrust (needs BRAINTRUST_API_KEY).",
    )
    parser.add_argument(
        "--eval-run-id",
        default=None,
        help="Optional correlation id for the Braintrust row.",
    )
    args = parser.parse_args()

    emit_eval = args.eval or os.environ.get("AUTO_PROMPT_CONTEXT_EVAL", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    path = PromptMethodsContext(data_root=args.data_root).build_context(
        emit_context_engineering_eval=emit_eval,
        eval_run_id=args.eval_run_id,
    )
    print(path)
