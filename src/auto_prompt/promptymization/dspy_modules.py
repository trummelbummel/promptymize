"""DSPy modules for summarizing and deduplicating prompt-method content."""

from __future__ import annotations

import re

import dspy

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor

_ATX_HEADER_START = re.compile(r"^#{1,6}\s")


class SummarizePromptMethods(dspy.Signature):
    """
    #### CONTEXT

    You summarize source text about prompt engineering into structured Markdown
    so downstream agents can apply it as concrete rules.

    #### OBJECTIVE

    Produce Markdown where **each distinct prompting method** is exactly one
    ATX section headed with ``##`` (method name). Under each header, use
    **indented bullet points** that state **actionable rules**—things a user or
    LLM can do to improve a prompt (not vague prose).

    #### STYLE

    - Headers: ``## <Short method name>`` only (no ``#`` top-level title in the summary).
    - Bullets: ``- `` lines; one idea per bullet; prefer imperative phrasing
      (e.g. "State the desired output format explicitly.").
    - Separate methods with a blank line between sections.

    #### AUDIENCE

    An agent will read this summary to **modify or score prompts** using these rules.

    Return **only** the Markdown summary string (no preamble, no code fences).
    """

    text: str = dspy.InputField(
        desc="Source text (e.g. scraped article) describing prompting techniques.",
    )
    summary: str = dspy.OutputField(
        desc=(
            "Markdown only: ## headers per method, bullet rules under each, "
            "no duplicate method headers, no filler outside Markdown."
        ),
    )


class MergeSimilarPromptMethods(dspy.Signature):
    """
    #### CONTEXT

    You receive Markdown where each ``##`` section describes one prompt-engineering
    method or rule set. Some sections may overlap in meaning even if the titles differ.

    #### OBJECTIVE

    Merge **semantically similar** sections into a single section per distinct method.
    Preserve unique rules; drop redundant bullets; unify naming so one ``##`` header
    captures the combined idea.

    #### STYLE

    - Output **only** Markdown.
    - Use ``##`` for each consolidated method (no top-level ``#`` title).
    - Bullets: ``- `` lines; imperative, actionable phrasing.

    #### AUDIENCE

    Downstream agents use this as a compact rulebook—avoid duplication across sections.
    """

    combined_sections: str = dspy.InputField(
        desc=(
            "Markdown sections (possibly separated by ---) that may describe overlapping "
            "prompt engineering methods."
        ),
    )
    merged_markdown: str = dspy.OutputField(
        desc=(
            "Consolidated Markdown: one ## section per distinct method, bullets merged "
            "without redundancy."
        ),
    )


class SemanticMethodMerger(dspy.Module):
    """LM pass that merges overlapping prompt-method sections into fewer sections."""

    def __init__(self) -> None:
        super().__init__()
        self.merge = dspy.ChainOfThought(MergeSimilarPromptMethods)

    def forward(self, text: str) -> dspy.Prediction:
        prediction = self.merge(combined_sections=text)
        return dspy.Prediction(merged_markdown=str(prediction.merged_markdown).strip())


class PromptMethodSummarizer(dspy.Module):
    """DSPy module that summarizes free-form text into structured Markdown."""

    def __init__(self) -> None:
        super().__init__()
        self.summarize = dspy.ChainOfThought(SummarizePromptMethods)

    def forward(self, text: str) -> dspy.Prediction:
        """
        Summarize ``text`` and return both headers and full sections.

        The returned :class:`dspy.Prediction` contains:

        - ``summary``: the full Markdown summary string.
        - ``headers``: a list of header lines (e.g. ``\"## Method\"``).
        - ``sections``: a list of strings, one per header-delimited section.

        :param text: The input text describing prompting methods to summarize.
        :return: Prediction with the Markdown summary, headers and header-delimited sections.
        """

        prediction = self.summarize(text=text)
        sections = HtmlPreprocessor.split_on_headers(prediction.summary)
        headers: list[str] = []
        for section in sections:
            if not section.strip():
                continue
            first = section.splitlines()[0].strip()
            if _ATX_HEADER_START.match(first):
                headers.append(first)
        return dspy.Prediction(
            summary=prediction.summary,
            headers=headers,
            sections=sections,
        )


class FindMatchingHeader(dspy.Signature):
    """Given a new Markdown section and the full text of an existing reference file,
    determine whether the reference file already contains a section that covers the
    same prompting method.

    Return the exact Markdown header line from the reference file if a match exists,
    or the string "NONE" if no matching section is found.
    """

    new_section: str = dspy.InputField(
        desc="A single Markdown section (header + bullet points) from the new input.",
    )
    reference_file: str = dspy.InputField(
        desc="The full Markdown content of the existing reference file.",
    )
    markdown_header: str = dspy.OutputField(
        desc='The matching header line from the reference file, or "NONE" if no match.',
    )


class FindNovelBullets(dspy.Signature):
    """Compare bullet points under a new section against the bullet points already
    present under the matching section in the reference file.

    Return only the bullet points from the new section that are NOT already
    mentioned—either verbatim or in similar form—in the reference section.
    Format the output as the Markdown header followed by only the novel bullet
    points.  Return "NONE" if every bullet point is already covered.
    """

    new_section: str = dspy.InputField(
        desc="The new Markdown section whose bullets should be checked.",
    )
    reference_section: str = dspy.InputField(
        desc="The existing Markdown section from the reference file to compare against.",
    )
    novel_bullets: str = dspy.OutputField(
        desc='The markdown header followed by novel bullet points only, or "NONE" if all are duplicates.',
    )


class DeduplicatePromptSection(dspy.Module):
    """Find bullet points in ``new_text`` that are not yet covered by ``reference_file``.

    For each header-delimited section in the new input the module:

    1. Asks the LM whether the reference file has a section about the same
       prompting method (``FindMatchingHeader``).
    2. If a match is found, extracts the corresponding reference section and
       asks the LM which bullets are genuinely novel (``FindNovelBullets``).
    3. Sections with no match in the reference are returned in full.

    The returned :class:`dspy.Prediction` contains:
    - ``novel_content``: a Markdown string with only novel headers + bullets.
    - ``sections``: the list of individual novel section strings.
    """

    def __init__(self) -> None:
        super().__init__()
        self.find_header = dspy.ChainOfThought(FindMatchingHeader)
        self.find_novel = dspy.ChainOfThought(FindNovelBullets)

    def forward(self, new_text: str, reference_file: str) -> dspy.Prediction:
        """
        Return only the parts of ``new_text`` not already in ``reference_file``.

        For each header-delimited section in ``new_text`` this method:

        1. Uses ``find_header`` to locate a matching section in ``reference_file``.
        2. If a match exists, calls ``find_novel`` to keep only genuinely new bullets.
        3. Drops sections whose bullets are fully covered by the reference.

        :param new_text: New Markdown content that may contain novel sections or bullets.
        :param reference_file: Existing Markdown reference file to compare against.
        :return: Prediction with ``novel_content`` (Markdown string) and ``sections`` (list of novel sections).
        """

        new_sections = HtmlPreprocessor.split_on_headers(new_text)
        ref_sections = HtmlPreprocessor.split_on_headers(reference_file)
        ref_by_header = {s.splitlines()[0].strip(): s for s in ref_sections}

        novel_parts: list[str] = []

        for section in new_sections:
            header_pred = self.find_header(
                new_section=section,
                reference_file=reference_file,
            )
            matched_header = header_pred.markdown_header.strip()

            if matched_header == "NONE" or matched_header not in ref_by_header:
                novel_parts.append(section)
                continue

            ref_section = ref_by_header[matched_header]
            novel_pred = self.find_novel(
                new_section=section,
                reference_section=ref_section,
            )
            bullets = novel_pred.novel_bullets.strip()

            if bullets and bullets != "NONE":
                novel_parts.append(bullets)

        novel_content = "\n\n".join(novel_parts)
        return dspy.Prediction(novel_content=novel_content, sections=novel_parts)
