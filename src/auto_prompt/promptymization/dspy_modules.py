from __future__ import annotations

import dspy

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor


class SummarizePromptMethods(dspy.Signature):
    """Summarize the provided text into well-structured Markdown.

    The output must use appropriate headers that describe the name of the prompting
    method (##, ###), bullet points around what is discussed on this prompting method should
    capture the main ideas so that they can be easily applied by an llm as rules.
    """

    text: str = dspy.InputField(desc="The source text to summarize.")
    summary: str = dspy.OutputField(
        desc="A Markdown-formatted summary with headers and bullet points.",
    )


class TextSummarizer(dspy.Module):
    """DSPy module that summarizes free-form text into structured Markdown."""

    def __init__(self) -> None:
        super().__init__()
        self.summarize = dspy.ChainOfThought(SummarizePromptMethods)

    def forward(self, text: str) -> dspy.Prediction:
        """Summarize ``text`` and return sections split on Markdown headers.

        The returned :class:`dspy.Prediction` contains:
        - ``summary``: the full Markdown summary string.
        - ``sections``: a list of strings, one per header-delimited section.
        """

        prediction = self.summarize(text=text)
        sections = HtmlPreprocessor.split_on_headers(prediction.summary)
        return dspy.Prediction(summary=prediction.summary, sections=sections)


# ---------------------------------------------------------------------------
# Deduplication module
# ---------------------------------------------------------------------------


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
        """Return only the parts of ``new_text`` not already in ``reference_file``."""

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
