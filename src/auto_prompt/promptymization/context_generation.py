from __future__ import annotations

import csv
import errno
import logging
import os
import re
import shutil
import time
import uuid
from collections.abc import Iterator
from pathlib import Path

import dspy

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore[assignment, misc]

from auto_prompt.errors import ConcurrencyError
from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor
from auto_prompt.preprocessing.dedupe_markdown import exact_dedupe_prompt_method_markdown
from auto_prompt.promptymization.dspy_lm import configure_dspy_lm_from_env
from auto_prompt.promptymization.dspy_modules import PromptMethodSummarizer

CONTEXT_FILENAME = "prompt_methods_context.csv"
CONTEXT_LOCK_FILENAME = f".{CONTEXT_FILENAME.removesuffix('.csv')}.lock"
MODEL_TYPE_ALL = "all"
CSV_COLUMNS = ("method_name", "model_type", "section_markdown")

_MODEL_TYPE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("claude", re.compile(r"\bclaude\b", re.I)),
    ("gpt", re.compile(r"\b(chatgpt|openai|gpt-?\d*\.?\d*)\b", re.I)),
    ("gemini", re.compile(r"\bgemini\b", re.I)),
    ("llama", re.compile(r"\b(llama|llama\d+)\b", re.I)),
    ("mistral", re.compile(r"\bmistral\b", re.I)),
    ("qwen", re.compile(r"\bqwen\b", re.I)),
    ("deepseek", re.compile(r"\bdeepseek\b", re.I)),
)

logger = logging.getLogger(__name__)


class PromptMethodsContext:
    """
    Merge summarizations into the canonical context CSV under ``sources/data/context``.

    Summarizes each discovered ``.md`` with :class:`PromptMethodSummarizer`, optionally runs an
    **incremental** deduplicator (e.g. :class:`~auto_prompt.promptymization.dspy_modules.DeduplicatePromptSection`) for the **current run**,
    **merges** the run output with any existing context rows,
    applies **exact** Markdown deduplication on combined sections, optionally moves
    processed folders under ``sources/data/processed``, and writes the result to
    ``sources/data/context/prompt_methods_context.csv``.

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
        # Only the default summarizer requires DSPy LM configuration.
        self._needs_dspy_lm_config = summarizer is None or incremental_deduplicator is not None
        self.summarizer: dspy.Module = summarizer or PromptMethodSummarizer()
        self.incremental_deduplicator: dspy.Module | None = incremental_deduplicator

    def build_context(
        self,
        *,
        emit_context_engineering_eval: bool = False,
        eval_run_id: str | None = None,
        lock_timeout_seconds: float = 30.0,
        chunk_long_sources: bool = True,
        max_chunk_chars: int = 12000,
    ) -> Path:
        """
        Run summarization over Markdown files, move processed folders, write context CSV.

        Discovers ``*.md`` under ``data_root`` excluding ``processed`` and ``context``,
        calls the summarizer on each file, aggregates ``summary`` strings, moves each
        containing folder into ``processed`` once per folder, and **merges** this run's
        aggregate into the existing canonical context rows.

        :param emit_context_engineering_eval: If ``True``, log a ``context_engineering`` row
            to Braintrust after the merge (requires ``BRAINTRUST_API_KEY`` and related env).
        :param eval_run_id: Optional correlation id for the eval record.
        :return: Path to ``prompt_methods_context.csv``.
        """

        self.processed_root.mkdir(parents=True, exist_ok=True)
        self.context_root.mkdir(parents=True, exist_ok=True)

        latest_path = self.context_root / CONTEXT_FILENAME
        lock_path = self.context_root / CONTEXT_LOCK_FILENAME

        lock_fd: int | None = None
        try:
            lock_fd = self._acquire_merge_lock(lock_path=lock_path, timeout_seconds=lock_timeout_seconds)

            existing_markdown = self._markdown_from_existing_csv(latest_path)

            markdown_files = list(self._iter_markdown_files())
            if not markdown_files:
                markdown_files = list(self._iter_processed_markdown_files())
                if markdown_files:
                    logger.info(
                        "No unprocessed markdown found under %s; using processed sources fallback (%d files).",
                        self.data_root,
                        len(markdown_files),
                    )
            if self._needs_dspy_lm_config and markdown_files:
                configure_dspy_lm_from_env()

            aggregated, running_reference, source_rel_paths = self._summarize_and_stage_sources(
                markdown_files,
                chunk_long_sources=chunk_long_sources,
                max_chunk_chars=max_chunk_chars,
            )
            merged_markdown = self._build_context_body(
                existing=existing_markdown,
                aggregated=aggregated,
                running_reference=running_reference,
            )
            csv_text = self._render_context_csv(merged_markdown)
            self._atomic_write_text(latest_path=latest_path, text=csv_text)
        finally:
            if lock_fd is not None:
                self._release_merge_lock(lock_path=lock_path, lock_fd=lock_fd)

        if emit_context_engineering_eval:
            from auto_prompt.evaluation.config import load_braintrust_config_from_env
            from auto_prompt.evaluation.logging import build_context_engineering_record, log_step

            record = build_context_engineering_record(
                run_id=eval_run_id,
                data_root=str(self.data_root.resolve()),
                context_path=str(latest_path.resolve()),
                source_paths=source_rel_paths,
                merged_body=merged_markdown,
                incremental_dedupe=self.incremental_deduplicator is not None,
            )
            log_step(record, config=load_braintrust_config_from_env())

        return latest_path

    def _lock_file_holder_alive(self, lock_path: Path) -> bool | None:
        """
        Return whether the PID stored in ``lock_path`` appears to be running.

        ``False`` means the lock is stale (safe to remove). ``None`` means we could
        not tell (treat as *held* by another live process).

        Used only for the non-``fcntl`` fallback (platforms without advisory locking).
        """

        try:
            raw = lock_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if not raw:
            return False
        try:
            pid = int(raw.split()[0])
        except ValueError:
            return False
        if pid == os.getpid():
            return True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            # Another user's process may hold the lock; do not steal it.
            return True
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                return False
            return None
        return True

    def _acquire_merge_lock_flock(self, *, lock_path: Path, timeout_seconds: float) -> int:
        """
        POSIX advisory lock: released automatically when the holding process exits,
        so crashed builds do not leave an indefinite ``O_EXCL`` stale lock.
        """

        assert fcntl is not None
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_WRONLY, 0o644)
        start = time.monotonic()
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() - start >= timeout_seconds:
                    try:
                        os.close(lock_fd)
                    except OSError:
                        pass
                    raise ConcurrencyError("Context merge lock not acquired within timeout.")
                time.sleep(0.1)
        try:
            os.ftruncate(lock_fd, 0)
            os.write(lock_fd, str(os.getpid()).encode("utf-8"))
            os.fsync(lock_fd)
        except Exception:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                os.close(lock_fd)
            except OSError:
                pass
            raise
        return lock_fd

    def _acquire_merge_lock_oexcl(self, *, lock_path: Path, timeout_seconds: float) -> int:
        """Fallback when ``fcntl`` is unavailable (e.g. Windows): ``O_EXCL`` + stale PID cleanup."""

        start = time.monotonic()
        while True:
            try:
                lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                os.write(lock_fd, str(os.getpid()).encode("utf-8"))
                return lock_fd
            except FileExistsError:
                alive = self._lock_file_holder_alive(lock_path)
                if alive is False:
                    try:
                        lock_path.unlink(missing_ok=True)
                    except OSError:
                        pass
                    continue
                if time.monotonic() - start >= timeout_seconds:
                    raise ConcurrencyError("Context merge lock not acquired within timeout.")
                time.sleep(0.1)

    def _acquire_merge_lock(self, *, lock_path: Path, timeout_seconds: float) -> int:
        """
        Acquire an exclusive lock for writing ``prompt_methods_context.csv``.

        On POSIX, uses ``fcntl.flock`` so locks are released when the holder process
        terminates. Else falls back to ``O_EXCL`` plus best-effort stale PID removal.
        """

        if fcntl is not None:
            return self._acquire_merge_lock_flock(lock_path=lock_path, timeout_seconds=timeout_seconds)
        return self._acquire_merge_lock_oexcl(lock_path=lock_path, timeout_seconds=timeout_seconds)

    def _release_merge_lock(self, *, lock_path: Path, lock_fd: int) -> None:
        """Release a lock acquired via :meth:`_acquire_merge_lock`."""

        try:
            os.close(lock_fd)
        finally:
            try:
                lock_path.unlink(missing_ok=True)  # type: ignore[arg-type]
            except Exception:
                # Best-effort; merge correctness relies on the lock file creation semantics.
                pass

    def _atomic_write_text(self, *, latest_path: Path, text: str) -> None:
        """Write ``text`` to a temporary file and atomically replace ``latest_path``."""

        tmp = self.context_root / f".{latest_path.name}.{uuid.uuid4().hex}.tmp"
        with tmp.open("w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(latest_path)

    def _summarize_and_stage_sources(
        self,
        markdown_files: list[Path],
        *,
        chunk_long_sources: bool,
        max_chunk_chars: int,
    ) -> tuple[list[str], str, list[str]]:
        """
        Summarize each ``.md`` and move its source folder to ``processed``.

        :returns: ``(aggregated_summaries, running_reference, source_rel_paths)``.
        """

        aggregated: list[str] = []
        running_reference = ""
        moved: set[Path] = set()
        source_rel_paths: list[str] = []
        incremental = self.incremental_deduplicator is not None

        for md_path in markdown_files:
            source_rel_paths.append(str(md_path.relative_to(self.data_root)))
            text = md_path.read_text(encoding="utf-8")
            summary = self._summarize_source_text(
                text=text,
                chunk_long_sources=chunk_long_sources,
                max_chunk_chars=max_chunk_chars,
            )

            if incremental:
                deduped = self.incremental_deduplicator.forward(  # type: ignore[union-attr]
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

            if "processed" in md_path.relative_to(self.data_root).parts:
                # Already in processed tree (e.g., dev fixture fallback), do not re-stage.
                continue

            relative = folder.relative_to(self.data_root)
            target_folder = self.processed_root / relative
            target_folder.parent.mkdir(parents=True, exist_ok=True)
            if folder.exists():
                shutil.move(str(folder), str(target_folder))
                moved.add(folder)

        return aggregated, running_reference, source_rel_paths

    def _summarize_source_text(
        self,
        *,
        text: str,
        chunk_long_sources: bool,
        max_chunk_chars: int,
    ) -> str:
        """
        Summarize a single source markdown string, optionally chunking long inputs.
        """

        text = text.strip()
        if not text:
            return ""
        if not chunk_long_sources or max_chunk_chars <= 0 or len(text) <= max_chunk_chars:
            prediction = self.summarizer(text=text)
            return str(prediction.summary).strip()

        chunks = self._chunk_markdown(text=text, max_chunk_chars=max_chunk_chars)
        summaries: list[str] = []
        for chunk in chunks:
            prediction = self.summarizer(text=chunk)
            s = str(prediction.summary).strip()
            if s:
                summaries.append(s)
        return "\n\n".join(summaries).strip()

    def _chunk_markdown(self, *, text: str, max_chunk_chars: int) -> list[str]:
        """
        Split markdown into chunks that are roughly bounded by ``max_chunk_chars``.

        Prefers splitting on detected ATX headers; falls back to simple character slicing.
        """

        if max_chunk_chars <= 0:
            return [text]

        sections = HtmlPreprocessor.split_on_headers(text)
        if not sections:
            return [text]

        chunks: list[str] = []
        current_parts: list[str] = []
        current_len = 0

        def flush_current() -> None:
            nonlocal current_parts, current_len
            if current_parts:
                chunks.append("\n\n".join(current_parts).strip())
            current_parts = []
            current_len = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            if len(section) > max_chunk_chars:
                # Flush any accumulated content, then slice the long section.
                flush_current()
                for i in range(0, len(section), max_chunk_chars):
                    piece = section[i : i + max_chunk_chars].strip()
                    if piece:
                        chunks.append(piece)
                continue

            sep_len = 2 if current_parts else 0
            if current_len + sep_len + len(section) <= max_chunk_chars:
                current_parts.append(section)
                current_len += sep_len + len(section)
            else:
                flush_current()
                current_parts.append(section)
                current_len = len(section)

        flush_current()
        return [c for c in chunks if c.strip()]

    def _markdown_from_existing_csv(self, csv_path: Path) -> str:
        """
        Rebuild merged markdown from existing CSV rows.

        The CSV is exploded by model type, so this collapses duplicate
        ``section_markdown`` values before re-merging.
        """

        if not csv_path.exists():
            return ""

        seen: set[str] = set()
        ordered_sections: list[str] = []
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                section = str(row.get("section_markdown", "")).strip()
                if not section or section in seen:
                    continue
                seen.add(section)
                ordered_sections.append(section)
        return "\n\n".join(ordered_sections).strip()

    def _render_context_csv(self, merged_markdown: str) -> str:
        """
        Render canonical context CSV from merged markdown sections.
        """

        rows: list[dict[str, str]] = []
        for section in HtmlPreprocessor.split_on_headers(merged_markdown):
            section = section.strip()
            if not section:
                continue
            first_line = section.splitlines()[0].strip()
            method_name = re.sub(r"^#{1,6}\s*", "", first_line).strip() or "method"
            model_types = self._infer_model_types(section)
            for model_type in model_types:
                rows.append(
                    {
                        "method_name": method_name,
                        "model_type": model_type,
                        "section_markdown": section,
                    }
                )

        out = [",".join(CSV_COLUMNS)]
        for row in rows:
            out.append(
                ",".join(
                    [
                        self._csv_quote(row["method_name"]),
                        self._csv_quote(row["model_type"]),
                        self._csv_quote(row["section_markdown"]),
                    ]
                )
            )
        return "\n".join(out).strip() + "\n"

    def _infer_model_types(self, section_markdown: str) -> list[str]:
        """Infer applicable model-type labels from a section."""

        found: list[str] = []
        for label, pattern in _MODEL_TYPE_PATTERNS:
            if pattern.search(section_markdown):
                found.append(label)
        if not found:
            return [MODEL_TYPE_ALL]
        return sorted(set(found))

    def _csv_quote(self, value: str) -> str:
        """CSV-escape a single value."""

        escaped = value.replace('"', '""')
        return f'"{escaped}"'

    def _build_context_body(self, *, existing: str, aggregated: list[str], running_reference: str) -> str:
        """
        Merge a run's output into existing context sections.
        """

        merged = running_reference if self.incremental_deduplicator is not None else "\n\n".join(
            s.strip() for s in aggregated if s.strip()
        )
        chunk = exact_dedupe_prompt_method_markdown(merged) if merged.strip() else ""

        if not chunk.strip():
            return existing
        if not existing.strip():
            return chunk
        return exact_dedupe_prompt_method_markdown(f"{existing.rstrip()}\n\n{chunk.rstrip()}")

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

    def _iter_processed_markdown_files(self) -> Iterator[Path]:
        """Yield markdown files already under ``processed`` as a fallback source set."""
        if not self.processed_root.exists():
            return
        for md_path in sorted(self.processed_root.rglob("*.md")):
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

