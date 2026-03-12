from __future__ import annotations

import dspy

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor


class SummarizeText(dspy.Signature):
    """Summarize the provided text into well-structured Markdown.

    The output must use appropriate headers (##, ###), bullet points, and
    concise language so a reader can quickly grasp the key ideas.
    """

    text: str = dspy.InputField(desc="The source text to summarize.")
    summary: str = dspy.OutputField(
        desc="A Markdown-formatted summary with headers and bullet points.",
    )


class TextSummarizer(dspy.Module):
    """DSPy module that summarizes free-form text into structured Markdown."""

    def __init__(self) -> None:
        super().__init__()
        self.summarize = dspy.ChainOfThought(SummarizeText)

    def forward(self, text: str) -> dspy.Prediction:
        """Summarize ``text`` and return sections split on Markdown headers.

        The returned :class:`dspy.Prediction` contains:
        - ``summary``: the full Markdown summary string.
        - ``sections``: a list of strings, one per header-delimited section.
        """

        prediction = self.summarize(text=text)
        sections = HtmlPreprocessor.split_on_headers(prediction.summary)
        return dspy.Prediction(summary=prediction.summary, sections=sections)
