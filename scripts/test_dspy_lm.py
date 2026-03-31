from __future__ import annotations

import dspy

from auto_prompt.promptymization.dspy_lm import configure_dspy_lm_from_env


def main() -> None:
    # Configure global dspy.settings.lm from env (DSPY_MODEL, DSPY_API_BASE, DSPY_API_KEY, etc.)
    configure_dspy_lm_from_env(force=True)

    # Simple signature: ask the LM to answer a question
    class AnswerQuestion(dspy.Signature):
        """Answer a user question in one short paragraph."""
        question: str = dspy.InputField()
        answer: str = dspy.OutputField()

    lm = dspy.settings.lm
    print("Using LM:", getattr(lm, "model", None), lm.kwargs.get("api_base"))

    # Direct LM call
    raw = lm("Say hello from the configured DSPy LM.")
    print("Raw LM output:\n", raw)

    # Or via a small module
    module = dspy.Predict(AnswerQuestion)
    pred = module(question="What is this script testing?")
    print("\nStructured prediction:\n", pred.answer)


if __name__ == "__main__":
    main()