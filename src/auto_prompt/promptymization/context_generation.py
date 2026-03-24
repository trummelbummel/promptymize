from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import dspy

from auto_prompt.promptymization.dedupe_markdown import exact_dedupe_prompt_method_markdown
from auto_prompt.promptymization.dspy_modules import PromptMethodSummarizer

CONTEXT_FILENAME = "prompt_methods_context.md"


class PromptMethodsContext:
    """
    Merge summarizations into the canonical context Markdown under ``sources/data/context``.

    Summarizes each discovered ``.md`` with :class:`PromptMethodSummarizer`, optionally runs an
    **incremental** deduplicator (e.g. :class:`~auto_prompt.promptymization.dspy_modules.DeduplicatePromptSection`) for the **current run**,
    **merges** the run output with any existing ``prompt_methods_context.md``,
    applies **exact** Markdown deduplication on the combined text, optionally moves
    processed folders under ``sources/data/processed``, and writes the result to
    ``sources/data/context/prompt_methods_context.md``.

    :param summarizer: Optional summarizer; defaults to :class:`PromptMethodSummarizer`.
    :param data_root: Root directory containing scraped Markdown (default: ``<project>/sources/data``).
    :param incremental_deduplicator: If set, called as ``forward(new_text=summary, reference_file=accumulated)`` between files within the run (LM-assisted dedupe). If ``None``, only per-file summaries are concatenated for this run before merge.
    """

    def __init__(
        self,
        summarizer: dspy.Module | None = None,
        data_root: Path | None = None,
        incremental_deduplicator: dspy.Module | None = None,
    ) -> None:
        project_root = Path(__file__).resolve().parents[3]
        self.data_root = data_root if data_root is not None else project_root / "sources" / "data"
        self.processed_root = self.data_root / "processed"
        self.context_root = self.data_root / "context"
        self.summarizer: dspy.Module = summarizer or PromptMethodSummarizer()
        self.incremental_deduplicator: dspy.Module | None = incremental_deduplicator

    def build_context(
        self,
        *,
        emit_context_engineering_eval: bool = False,
        eval_run_id: str | None = None,
    ) -> Path:
        """
        Run summarization over Markdown files, move processed folders, write context file.

        Discovers ``*.md`` under ``data_root`` excluding ``processed`` and ``context``,
        calls the summarizer on each file, aggregates ``summary`` strings, moves each
        containing folder into ``processed`` once per folder, and **merges** this run's
        aggregate into ``prompt_methods_context.md`` (reading the prior file if present).

        :param emit_context_engineering_eval: If ``True``, log a ``context_engineering`` row
            to Braintrust after the merge (requires ``BRAINTRUST_API_KEY`` and related env).
        :param eval_run_id: Optional correlation id for the eval record.
        :return: Path to ``prompt_methods_context.md``.
        """

        self.processed_root.mkdir(parents=True, exist_ok=True)
        self.context_root.mkdir(parents=True, exist_ok=True)

        latest_path = self.context_root / CONTEXT_FILENAME
        existing = latest_path.read_text(encoding="utf-8") if latest_path.exists() else ""

        markdown_files = list(self._iter_markdown_files())
        aggregated: list[str] = []
        running_reference = ""
        moved: set[Path] = set()
        source_rel_paths: list[str] = []

        for md_path in markdown_files:
            source_rel_paths.append(str(md_path.relative_to(self.data_root)))
            text = md_path.read_text(encoding="utf-8")
            prediction = self.summarizer(text=text)
            summary = prediction.summary.strip()
            if self.incremental_deduplicator is not None:
                deduped = self.incremental_deduplicator.forward(
                    new_text=summary,
                    reference_file=running_reference,
                )
                piece = str(deduped.novel_content).strip()
                if piece:
                    running_reference = (
                        f"{running_reference}\n\n{piece}".strip()
                        if running_reference
                        else piece
                    )
            else:
                aggregated.append(summary)

            folder = md_path.parent
            if folder in moved:
                continue

            relative = folder.relative_to(self.data_root)
            target_folder = self.processed_root / relative
            target_folder.parent.mkdir(parents=True, exist_ok=True)
            if folder.exists():
                shutil.move(str(folder), str(target_folder))
                moved.add(folder)

        if self.incremental_deduplicator is not None:
            merged = running_reference
        else:
            merged = "\n\n".join(s.strip() for s in aggregated if s.strip())

        chunk = exact_dedupe_prompt_method_markdown(merged) if merged.strip() else ""

        if not chunk.strip():
            body = existing
        elif not existing.strip():
            body = chunk
        else:
            body = exact_dedupe_prompt_method_markdown(f"{existing.rstrip()}\n\n{chunk.rstrip()}")

        latest_path.write_text(body, encoding="utf-8")

        if emit_context_engineering_eval:
            from auto_prompt.evaluation.config import load_braintrust_config_from_env
            from auto_prompt.evaluation.logging import build_context_engineering_record, log_step

            record = build_context_engineering_record(
                run_id=eval_run_id,
                data_root=str(self.data_root.resolve()),
                context_path=str(latest_path.resolve()),
                source_paths=source_rel_paths,
                merged_body=body,
                incremental_dedupe=self.incremental_deduplicator is not None,
            )
            log_step(record, config=load_braintrust_config_from_env())

        return latest_path

    def _iter_markdown_files(self) -> Iterator[Path]:
        """
        Yield Markdown files under ``data_root`` that are not under excluded dirs.

        :return: Paths to ``.md`` files to process.
        """

        if not self.data_root.exists():
            return
        for md_path in sorted(self.data_root.rglob("*.md")):
            if self._is_excluded(md_path):
                continue
            yield md_path

    def _is_excluded(self, path: Path) -> bool:
        """
        Return whether ``path`` lies under ``processed`` or ``context``.

        :param path: Candidate file path.
        :return: True if the path should be skipped.
        """

        try:
            rel = path.relative_to(self.data_root)
        except ValueError:
            return True
        parts = rel.parts
        return "processed" in parts or "context" in parts

